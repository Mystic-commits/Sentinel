"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  Check,
  CheckCheck,
  ChevronRight,
  CircleHelp,
  Copy,
  File,
  FileImage,
  FileText,
  Folder,
  FolderOpen,
  History,
  LayoutGrid,
  LoaderCircle,
  Plus,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Terminal,
  X,
} from "lucide-react";
import { api } from "@/lib/api/client";
import "./workspace.css";

type Action = {
  type: string;
  source_path?: string;
  destination_path?: string;
  reason: string;
};
type Session = {
  task_id: string;
  state: string;
  summary: string;
  created_at: string;
  plan?: { scope_path: string; actions: Action[] };
  result?: { success?: number; failed?: number; error?: string };
  approved_actions?: number[];
  receipts?: {timestamp: string; event: string; action: Action}[];
  error?: string;
  planning_warning?: string;
  recovery_required?: boolean;
  demo?: boolean;
};
type Recipe = {
  name: string;
  description: string;
  prompt: string;
  icon: "files" | "image" | "archive";
};
const defaults: Recipe[] = [
  {
    name: "A fresh start",
    description: "Give a busy folder a clear structure.",
    prompt:
      "Group files by type into clearly named folders. Keep existing folders and all file contents unchanged. Do not delete anything.",
    icon: "files",
  },
  {
    name: "Paperwork, sorted",
    description: "Bring documents into one clear system.",
    prompt:
      "Organize documents into useful topic folders based on their names. Leave photos, code and existing folders alone. Do not delete anything.",
    icon: "archive",
  },
  {
    name: "Room for memories",
    description: "Separate screenshots from your photos.",
    prompt:
      "Group screenshots into a Screenshots folder and photos by year when the date is known. Leave everything else untouched. Do not delete anything.",
    icon: "image",
  },
];
const example: Session = {
  task_id: "sample-session",
  state: "review",
  summary: "A clearer home for six scattered files.",
  created_at: "",
  demo: true,
  plan: {
    scope_path: "Sample / Downloads",
    actions: [
      {
        type: "move",
        source_path: "Sample/Downloads/Brand brief.pdf",
        destination_path: "Sample/Downloads/Documents/Brand brief.pdf",
        reason: "A project document, grouped with your other paperwork.",
      },
      {
        type: "move",
        source_path: "Sample/Downloads/Invoice March.pdf",
        destination_path: "Sample/Downloads/Documents/Invoice March.pdf",
        reason: "Keep this invoice easy to find among your documents.",
      },
      {
        type: "move",
        source_path: "Sample/Downloads/Screenshot 2026-10-22.png",
        destination_path:
          "Sample/Downloads/Screenshots/Screenshot 2026-10-22.png",
        reason: "The filename identifies this as a screenshot.",
      },
      {
        type: "move",
        source_path: "Sample/Downloads/Weekend.jpg",
        destination_path: "Sample/Downloads/Images/Weekend.jpg",
        reason: "A photo, separated from working documents.",
      },
      {
        type: "move",
        source_path: "Sample/Downloads/Research notes.md",
        destination_path: "Sample/Downloads/Documents/Research notes.md",
        reason: "Text notes, grouped with your documents.",
      },
      {
        type: "move",
        source_path: "Sample/Downloads/Project assets.zip",
        destination_path: "Sample/Downloads/Archives/Project assets.zip",
        reason: "An archive, kept together and left intact.",
      },
    ],
  },
};
const basename = (value = "") => value.split(/[\\/]/).pop() || value;
const label = (state: string) =>
  ({
    review: "Ready to review",
    completed: "Completed",
    failed: "Needs attention",
    planning: "Preparing preview",
    executing: "Applying changes",
    scanning: "Scanning files",
  })[state] || state;
function FileIcon({ name }: { name: string }) {
  return /\.(png|jpg|jpeg)$/i.test(name) ? (
    <FileImage size={18} />
  ) : /\.(pdf|md|txt)$/i.test(name) ? (
    <FileText size={18} />
  ) : (
    <File size={18} />
  );
}

export default function Workspace() {
  const [view, setView] = useState<"workspace" | "recipes" | "history">(
    "workspace",
  );
  const [modal, setModal] = useState<"connect" | "terminal" | "search" | null>(
    null,
  );
  const [path, setPath] = useState("");
  const [prompt, setPrompt] = useState("");
  const [strategy, setStrategy] = useState<"local_ai" | "file_types">(
    "local_ai",
  );
  const [recipes, setRecipes] = useState<Recipe[]>(defaults);
  const [recent, setRecent] = useState<string[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [active, setActive] = useState<Session | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [tab, setTab] = useState<"changes" | "activity">("changes");
  const [connected, setConnected] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const dialog = useRef<HTMLDialogElement>(null);
  const goal = useRef<HTMLTextAreaElement>(null);
  const activeId = useRef<string | null>(null);
  const refreshing = useRef(false);
  const [historyError, setHistoryError] = useState("");
  const refresh = useCallback(async () => {
    if (refreshing.current) return;
    refreshing.current = true;
    try {
      try {
        const health = (await api.health()) as { database_connected: boolean };
        if (!health.database_connected) throw new Error("Local task storage is unavailable.");
        setConnected(true);
      } catch {
        setConnected(false);
        return;
      }
      const all: Session[] = [];
      let total = 0;
      do {
        const page = (await api.getTasks(all.length)) as { tasks: Session[]; total: number };
        total = page.total;
        if (!page.tasks.length) break;
        all.push(...page.tasks);
      } while (all.length < total);
      setSessions(all);
      const id = activeId.current;
      if (id) {
        const current = (await api.getTask(id)) as Session;
        if (activeId.current === id) setActive(current);
      }
      setHistoryError("");
    } catch (err) {
      setHistoryError(err instanceof Error ? err.message : "Session history could not be refreshed.");
    } finally {
      refreshing.current = false;
    }
  }, []);
  useEffect(() => {
    const initial = setTimeout(() => void refresh(), 0);
    const timer = setInterval(() => void refresh(), 4000);
    return () => {
      clearTimeout(initial);
      clearInterval(timer);
    };
  }, [refresh]);
  useEffect(() => {
    const hydrate = setTimeout(() => {
      try {
        const stored = localStorage.getItem("sentinel-recipes");
        if (stored) {
          const parsed: unknown = JSON.parse(stored);
          if (Array.isArray(parsed)) setRecipes([...defaults, ...parsed.filter((item): item is Recipe =>
            item && typeof item.name === "string" && typeof item.description === "string" && typeof item.prompt === "string" && ["files", "image", "archive"].includes(item.icon))]);
        }
        const folders = localStorage.getItem("sentinel-folders");
        if (folders) {
          const parsed: unknown = JSON.parse(folders);
          if (Array.isArray(parsed)) setRecent(parsed.filter((item): item is string => typeof item === "string").slice(0, 5));
        }
      } catch {
        /* Start with defaults if browser storage is unavailable. */
      }
    }, 0);
    return () => clearTimeout(hydrate);
  }, []);
  useEffect(() => {
    if (modal) {dialog.current?.showModal(); if(modal === "search") dialog.current?.querySelector("input")?.focus();}
    else dialog.current?.close();
  }, [modal]);
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        setModal("search");
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(""), 4000);
    return () => clearTimeout(timer);
  }, [notice]);
  const openSession = (item: Session) => {
    activeId.current = item.demo ? null : item.task_id;
    setActive(item);
    setSelected(item.approved_actions || []);
    setQuery("");
    setTab("changes");
    setView("workspace");
    setError("");
    if (!item.demo) {
      void api.getTask(item.task_id).then((result) => {
        if (activeId.current !== item.task_id) return;
        const detail = result as Session;
        setActive(detail);
        setSelected(detail.approved_actions || []);
      }).catch((err) => {
        if (activeId.current === item.task_id) setError(err instanceof Error ? err.message : "Could not load this session.");
      });
    }
  };
  const newSession = () => {
    setPrompt("");
    setPath("");
    setStrategy("local_ai");
    activeId.current = null;
    setActive(null);
    setSelected([]);
    setView("workspace");
    setError("");
  };
  const chooseRecipe = (recipe: Recipe) => {
    newSession();
    setStrategy("local_ai");
    setPrompt(recipe.prompt);
    setNotice(
      `“${recipe.name}” is ready. Choose a folder, then create your preview.`,
    );
    goal.current?.focus();
  };
  const rememberFolder = () => {
    const folders = [
      path.trim(),
      ...recent.filter((item) => item !== path.trim()),
    ].slice(0, 5);
    setRecent(folders);
    try {
      localStorage.setItem("sentinel-folders", JSON.stringify(folders));
    } catch {
      setNotice(
        "Browser storage is unavailable; this folder will not be remembered.",
      );
    }
  };
  const createPlan = async () => {
    if (!path.trim() || !prompt.trim()) {
      setError("Choose a folder and describe how you want it organized.");
      return;
    }
    if (!connected) {
      setModal("connect");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = (await api.createPlan(
        prompt.trim(),
        path.trim(),
        strategy,
      )) as { task_id: string };
      rememberFolder();
      openSession({
        task_id: result.task_id,
        state: "planning",
        summary: prompt,
        created_at: new Date().toISOString(),
      });
      await refresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not create the preview. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  };
  const saveRecipe = () => {
    if (!prompt.trim()) {
      setError("Write your organization instructions before saving a recipe.");
      return;
    }
    if (recipes.some((item) => item.prompt === prompt.trim())) {
      setNotice("This recipe is already in your library.");
      return;
    }
    const custom = {
      name: prompt.trim().slice(0, 34),
      description: "Your saved organization instructions.",
      prompt: prompt.trim(),
      icon: "files" as const,
    };
    const next = [...recipes, custom];
    try {
      localStorage.setItem(
        "sentinel-recipes",
        JSON.stringify(next.slice(defaults.length)),
      );
      setRecipes(next);
      setNotice("Recipe saved to this browser.");
    } catch {
      setError(
        "Browser storage is unavailable. The recipe could not be saved.",
      );
    }
  };
  const apply = async () => {
    if (!active || !selected.length || busy) return;
    setBusy(true);
    setError("");
    try {
      if (active.demo) {
        setActive({
          ...active,
          state: "completed",
          result: { success: selected.length, failed: 0 },
        });
        setNotice("Sample complete. No real files were changed.");
      } else {
        await api.executeTask(active.task_id, selected);
        setActive({ ...active, state: "executing" });
        await refresh();
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Changes could not be applied.",
      );
    } finally {
      setBusy(false);
    }
  };
  const [confirming, setConfirming] = useState(false);
  const confirmation = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (confirming) confirmation.current?.showModal();
    else confirmation.current?.close();
  }, [confirming]);
  const exportSession = () => {
    if (!active) return;
    const blob = new Blob([JSON.stringify(active, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `sentinel-${active.task_id}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    setNotice("Session report exported.");
  };
  const copy = async (value: string) => {
    try {
      await navigator.clipboard.writeText(value);
      setNotice("Copied to clipboard.");
    } catch {
      setError(
        "Clipboard access is unavailable. Select and copy the command manually.",
      );
    }
  };
  const actions = active?.plan?.actions || [];
  const filtered = actions
    .map((action, index) => ({ action, index }))
    .filter(({ action }) =>
      `${action.source_path} ${action.destination_path} ${action.reason}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    );
  const counts = {
    review: sessions.filter((item) => item.state === "review").length,
    completed: sessions.filter((item) => item.state === "completed").length,
  };
  return (
    <div className="sentinel-workspace">
      <aside className="sw-sidebar">
        <button className="sw-brand" onClick={newSession}>
          <span className="sw-mark">
            <ShieldCheck size={21} />
          </span>
          sentinel<span className="sw-beta">PREVIEW</span>
        </button>
        <button className="sw-new" onClick={newSession}>
          <Plus size={16} /> New session
        </button>
        <nav aria-label="Workspace navigation">
          <button
            className={view === "workspace" ? "active" : ""}
            onClick={() => setView("workspace")}
          >
            <LayoutGrid size={17} /> Workspace
          </button>
          <button
            className={view === "recipes" ? "active" : ""}
            onClick={() => setView("recipes")}
          >
            <Sparkles size={17} /> Recipes <span>{recipes.length}</span>
          </button>
          <button
            className={view === "history" ? "active" : ""}
            onClick={() => setView("history")}
          >
            <History size={17} /> Session history <span>{sessions.length}</span>
          </button>
        </nav>
        <div className="sw-side-label">
          RECENT SESSIONS{" "}
          <button
            aria-label="Refresh session history"
            onClick={() => void refresh()}
          >
            <History size={13} />
          </button>
        </div>
        <div className="sw-recent">
          {sessions.slice(0, 6).map((item) => (
            <button key={item.task_id} onClick={() => openSession(item)}>
              <span className={`sw-state-dot ${item.state}`} />
              <span>{item.summary}</span>
            </button>
          ))}
          {!sessions.length && (
            <p>
              Your sessions will appear here.
              <br />A clear record of every change.
            </p>
          )}
        </div>
        <div className="sw-side-bottom">
          <button onClick={() => setModal("terminal")}>
            <Terminal size={16} /> Terminal access <ArrowUpRight size={14} />
          </button>
          <button onClick={() => setModal("connect")}>
            <span
              className={`sw-state-dot ${connected ? "completed" : "failed"}`}
            />
            <span>
              Local agent
              <small>
                {connected
                  ? "Connected to your device"
                  : "Waiting for connection"}
              </small>
            </span>
            <Settings2 size={15} />
          </button>
        </div>
      </aside>
      <div className="sw-shell">
        <header className="sw-header">
          <div>
            Personal workspace <ChevronRight size={13} />
            <strong>
              {view === "recipes"
                ? "Recipe library"
                : view === "history"
                  ? "Session history"
                  : "Overview"}
            </strong>
          </div>
          <button
            className="sw-search-trigger"
            onClick={() => setModal("search")}
          >
            <Search size={15} /> Find a session <kbd>⌘ K</kbd>
          </button>
          <button
            className="sw-help"
            aria-label="Connection help"
            onClick={() => setModal("connect")}
          >
            <CircleHelp size={18} />
          </button>
        </header>
        <main className="sw-content">
          {view === "workspace" && !active && (
            <>
              <div className="sw-eyebrow">
                <span /> YOUR FILES. A LITTLE MORE CONSIDERED.
              </div>
              <div className="sw-heading-row">
                <div>
                  <h1>
                    Less searching.
                    <br />
                    <em>More space to think.</em>
                  </h1>
                  <p>
                    Turn scattered files into a workspace that makes sense.
                    <br />
                    Local intelligence. A clear plan. Always your decision.
                  </p>
                </div>
                <div className="sw-orbit" aria-hidden="true">
                  <div className="orbit-file one">
                    <FileText />
                  </div>
                  <div className="orbit-file two">
                    <FileImage />
                  </div>
                  <div className="orbit-file three">
                    <File />
                  </div>
                  <div className="orbit-folder">
                    <FolderOpen size={47} />
                  </div>
                  <span>Everything in its place.</span>
                </div>
              </div>
              <div className="sw-section-heading">
                <h2>What would you like to put in order?</h2>
                <button onClick={() => setView("recipes")}>
                  View all recipes <ArrowRight size={14} />
                </button>
              </div>
              <div className="sw-recipes">
                {recipes.slice(0, 3).map((recipe, i) => (
                  <button
                    key={recipe.name}
                    className="sw-recipe"
                    onClick={() => chooseRecipe(recipe)}
                  >
                    <span className={`sw-recipe-icon tone-${i}`}>
                      {recipe.icon === "image" ? (
                        <FileImage size={21} />
                      ) : recipe.icon === "archive" ? (
                        <FileText size={21} />
                      ) : (
                        <FolderOpen size={21} />
                      )}
                    </span>
                    <ArrowUpRight className="recipe-arrow" size={17} />
                    <strong>{recipe.name}</strong>
                    <p>{recipe.description}</p>
                  </button>
                ))}
              </div>
              <section className="sw-composer" aria-label="Create a preview">
                <div className="sw-composer-title">
                  <span>
                    <Sparkles size={17} /> Or, make it your own.
                  </span>
                  <label className="sw-strategy">
                    Planning with{" "}
                    <select
                      aria-label="Planning mode"
                      value={strategy}
                      onChange={(e) => {
                        const value = e.target.value as
                          "local_ai" | "file_types";
                        setStrategy(value);
                        if (value === "file_types")
                          setPrompt(
                            "Group top-level documents, images, audio, videos and archives by file type. No deletions. Existing folders and other file types stay unchanged.",
                          );
                      }}
                    >
                      <option value="local_ai">Local AI</option>
                      <option value="file_types">
                        File type rules · no model
                      </option>
                    </select>
                  </label>
                </div>
                <label className="sw-sr" htmlFor="instructions">
                  Organization instructions
                </label>
                <textarea
                  readOnly={strategy === "file_types"}
                  id="instructions"
                  ref={goal}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Tell me what a more organized workspace looks like for you…"
                  onKeyDown={(e) => {
                    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
                      e.preventDefault();
                      void createPlan();
                    }
                  }}
                />
                <div className="sw-composer-tools">
                  <div className="sw-path">
                    <Folder size={16} />
                    <label className="sw-sr" htmlFor="scope">
                      Folder path
                    </label>
                    <input
                      id="scope"
                      list="recent-folders"
                      placeholder="Paste a folder path"
                      value={path}
                      onChange={(e) => setPath(e.target.value)}
                    />
                    <datalist id="recent-folders">
                      {recent.map((item) => (
                        <option key={item} value={item} />
                      ))}
                    </datalist>
                  </div>
                  <button
                    className="sw-text-button"
                    disabled={strategy === "file_types"}
                    onClick={saveRecipe}
                  >
                    Save recipe
                  </button>
                  <button
                    className="sw-primary"
                    disabled={busy || !path.trim() || !prompt.trim()}
                    onClick={() => void createPlan()}
                  >
                    {busy ? (
                      <LoaderCircle size={16} className="sw-spin" />
                    ) : (
                      <Sparkles size={15} />
                    )}{" "}
                    Create preview <ArrowRight size={15} />
                  </button>
                </div>
              </section>
              <div className="sw-composer-foot">
                <span>
                  <ShieldCheck size={14} /> Your files stay on your device.
                </span>
                <span>
                  {connected ? (
                    "Local agent connected · ⌘ / Ctrl + Enter"
                  ) : (
                    <button onClick={() => setModal("connect")}>
                      Agent offline · Connection guide ↗
                    </button>
                  )}
                </span>
              </div>
              <div className="sw-sample">
                <div>
                  <span className="sw-mini-label">GET A FEEL FOR IT</span>
                  <h3>A clearer Downloads folder, in six moves.</h3>
                  <p>
                    Explore a sample plan. Review the reasoning. Try selecting
                    changes.
                  </p>
                </div>
                <button
                  onClick={() =>
                    openSession({
                      ...example,
                      created_at: new Date().toISOString(),
                    })
                  }
                >
                  Try the sample workspace <ArrowRight size={16} />
                </button>
              </div>
            </>
          )}
          {view === "recipes" && (
            <>
              <div className="sw-eyebrow">YOUR REPEATABLE WORKFLOWS</div>
              <h1>
                A good system.
                <br />
                <em>Ready to use again.</em>
              </h1>
              <p className="sw-lead">
                Start with a considered recipe, or save your own instructions
                from the workspace.
              </p>
              <div className="sw-recipes sw-library">
                {recipes.map((recipe, i) => (
                  <article key={recipe.name} className="sw-recipe">
                    <span className={`sw-recipe-icon tone-${i % 3}`}>
                      <FolderOpen size={21} />
                    </span>
                    <strong>{recipe.name}</strong>
                    <p>{recipe.description}</p>
                    <button
                      className="sw-text-button"
                      onClick={() => chooseRecipe(recipe)}
                    >
                      Use recipe <ArrowRight size={14} />
                    </button>
                    {i >= 3 && (
                      <button
                        className="sw-text-button"
                        onClick={() => {
                          const next = recipes.filter((_, n) => n !== i);
                          try {
                            localStorage.setItem(
                              "sentinel-recipes",
                              JSON.stringify(next.slice(3)),
                            );
                            setRecipes(next);
                          } catch {
                            setError("Could not update browser storage.");
                          }
                        }}
                      >
                        Remove saved recipe
                      </button>
                    )}
                  </article>
                ))}
              </div>
            </>
          )}
          {view === "history" && (
            <>
              <div className="sw-eyebrow">A RECORD YOU CAN FOLLOW</div>
              <h1>
                Every session.
                <br />
                <em>Nothing out of sight.</em>
              </h1>
              <div className="sw-history-stats">
                <span>
                  <b>{sessions.length}</b> total sessions
                </span>
                <span>
                  <b>{counts.review}</b> waiting for review
                </span>
                <span>
                  <b>{counts.completed}</b> completed
                </span>
              </div>
              <div className="sw-filter">
                <Search size={16} />
                <input
                  aria-label="Search history"
                  placeholder="Search your sessions…"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                <button onClick={() => void refresh()}>Refresh</button>
              </div>
              <div className="sw-history-list">
                {sessions
                  .filter((item) =>
                    item.summary.toLowerCase().includes(search.toLowerCase()),
                  )
                  .map((item) => (
                    <button
                      key={item.task_id}
                      onClick={() => openSession(item)}
                    >
                      <FolderOpen size={21} />
                      <div>
                        <strong>{item.summary}</strong>
                        <small>
                          {new Date(item.created_at).toLocaleString()}
                        </small>
                      </div>
                      <span className="sw-status">{label(item.state)}</span>
                      <ChevronRight size={16} />
                    </button>
                  ))}
                {!sessions.length && (
                  <div className="sw-empty">
                    <History size={28} />
                    <h3>Your history starts with your first session.</h3>
                    <p>
                      Connect the local agent or explore the sample workspace.
                    </p>
                    <button
                      className="sw-primary"
                      onClick={() =>
                        openSession({
                          ...example,
                          created_at: new Date().toISOString(),
                        })
                      }
                    >
                      Explore sample <ArrowRight size={14} />
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
          {view === "workspace" && active && (
            <>
              <button className="sw-text-button sw-back" onClick={newSession}>
                ← Back to workspace
              </button>
              <div className="sw-eyebrow">
                {active.demo
                  ? "SAMPLE WORKSPACE · NO REAL FILES"
                  : "LOCAL SESSION"}
              </div>
              <div className="sw-review-heading">
                <div>
                  <h1>
                    {active.state === "completed"
                      ? "A little more order."
                      : "Your next move."}
                  </h1>
                  <p className="sw-lead">{active.summary}</p>
                </div>
                <span className="sw-status">{label(active.state)}</span>
              </div>
              <div className="sw-plan-info">
                <FolderOpen size={17} />
                <span>{active.plan?.scope_path || path}</span>
                <button onClick={exportSession}>
                  <ArrowDownToLine size={15} /> Export report
                </button>
              </div>
              {active.planning_warning && (
                <p className="sw-alert" role="status">
                  {active.planning_warning}
                </p>
              )}
              {active.recovery_required && (
                <p className="sw-alert">
                  This session was interrupted. Inspect its receipts and your
                  files before creating a new plan. It will not be replayed
                  automatically.
                </p>
              )}
              {active.state === "completed" && (
                <div className="sw-success">
                  <CheckCheck size={22} />
                  <div>
                    <strong>
                      {active.result?.success || 0}{" "}
                      {active.demo
                        ? "sample changes explored"
                        : active.result?.success === 1 ? "change completed" : "changes completed"}
                    </strong>
                    <p>
                      {active.demo
                        ? "No real files were accessed or changed."
                        : `${active.result?.failed || 0} operations reported a failure. Review the report for details.`}
                    </p>
                  </div>
                </div>
              )}
              {(active.result?.error || active.error) && (
                <p className="sw-alert" role="alert">
                  {active.result?.error || active.error}
                </p>
              )}
              {!active.plan && (
                <div className="sw-empty">
                  <LoaderCircle className={active.state === "failed" ? "" : "sw-spin"} size={28} />
                  <h3>{label(active.state)}</h3>
                  <p>
                    {active.state === "failed"
                      ? "The agent could not prepare this plan. Check your folder and model, then start a new session."
                      : "Your local agent is preparing the plan. This view refreshes automatically."}
                  </p>
                  <button
                    onClick={() => void refresh()}
                    className="sw-text-button"
                  >
                    Refresh now
                  </button>
                </div>
              )}
              {active.plan && (
                <>
                  <div className="sw-tabs">
                    <button
                      className={tab === "changes" ? "active" : ""}
                      onClick={() => setTab("changes")}
                    >
                      Proposed changes <span>{actions.length}</span>
                    </button>
                    <button
                      className={tab === "activity" ? "active" : ""}
                      onClick={() => setTab("activity")}
                    >
                      Activity & receipts
                    </button>
                  </div>
                  {tab === "changes" ? (
                    <>
                      <div className="sw-review-toolbar">
                        <div className="sw-filter">
                          <Search size={16} />
                          <input
                            aria-label="Search proposed changes"
                            placeholder="Find a file or destination…"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                          />
                        </div>
                        {active.state === "review" && (
                          <button
                            className="sw-text-button"
                            onClick={() =>
                              setSelected(
                                selected.length === actions.length
                                  ? []
                                  : actions.map((_, i) => i),
                              )
                            }
                          >
                            {actions.length > 0 &&
                            selected.length === actions.length
                              ? "Clear selection"
                              : "Select all changes"}
                          </button>
                        )}
                      </div>
                      <div className="sw-changes">
                        {filtered.map(({ action, index }) => (
                          <label
                            key={index}
                            className={`sw-change ${selected.includes(index) ? "selected" : ""}`}
                          >
                            <input
                              type="checkbox"
                              aria-label={`Select ${basename(action.source_path)}`}
                              checked={selected.includes(index)}
                              disabled={active.state !== "review"}
                              onChange={() =>
                                setSelected(
                                  selected.includes(index)
                                    ? selected.filter((i) => i !== index)
                                    : [...selected, index],
                                )
                              }
                            />
                            <span className="sw-file-icon">
                              <FileIcon name={action.source_path || ""} />
                            </span>
                            <span className="sw-file-detail">
                              <strong title={action.source_path}>
                                {basename(action.source_path) || "New folder"}
                              </strong>
                              <span>
                                <b>
                                  {action.type === "delete"
                                    ? "Move to system Trash"
                                    : action.type}
                                </b>
                                <ArrowRight size={12} />
                                {action.destination_path || "System Trash"}
                              </span>
                              <small>{action.reason}</small>
                            </span>
                            <span className="sw-change-number">
                              {String(index + 1).padStart(2, "0")}
                            </span>
                          </label>
                        ))}
                        {!filtered.length && (
                          <p className="sw-empty">
                            {actions.length
                              ? "No changes match your search."
                              : "No changes were proposed. Your files can stay as they are."}
                          </p>
                        )}
                      </div>
                      {active.state === "review" && (
                        <div className="sw-approval-bar">
                          <div>
                            <strong>
                              {selected.length} of {actions.length} selected
                            </strong>
                            <small>
                              Unselected files will stay exactly where they are.
                            </small>
                          </div>
                          <button
                            className="sw-primary"
                            disabled={!selected.length || busy}
                            onClick={() => setConfirming(true)}
                          >
                            Review & apply <ArrowRight size={15} />
                          </button>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="sw-activity">
                      <p>
                        <ShieldCheck size={16} /> Created{" "}
                        {new Date(active.created_at).toLocaleString()} ·{" "}
                        {label(active.state)}
                      </p>
                      {active.demo ? (
                        <p>
                          This is an interactive sample. No filesystem receipts
                          are generated.
                        </p>
                      ) : (
                        <div className="sw-receipt-list">{(active.receipts || []).map((receipt,index)=><article key={index}><span className="sw-receipt-icon">{receipt.event==='completed'?<Check size={16}/>:<History size={16}/>}</span><div><strong>{receipt.event==='completed'?'Change completed':'Change started'}</strong><p>{basename(receipt.action.source_path)} → {basename(receipt.action.destination_path)||'System Trash'}</p><time>{new Date(receipt.timestamp).toLocaleString()}</time></div></article>)}{!active.receipts?.length&&<p>No file operations have been recorded for this session.</p>}<details><summary>Technical receipt data</summary><pre>{JSON.stringify(active.receipts || [],null,2)}</pre></details></div>
                      )}
                    </div>
                  )}
                </>
              )}
            </>
          )}
          {(error || historyError) && (
            <div className="sw-alert" role="alert">
              {error || historyError}
              <button aria-label="Dismiss error" onClick={() => {setError(""); setHistoryError("");}}>
                <X size={15} />
              </button>
            </div>
          )}
          <footer className="sw-footer">
            <span>
              <ShieldCheck size={14} /> Considered by AI. Controlled by you.
            </span>
            <button onClick={() => setModal("terminal")}>
              <Terminal size={14} /> Also at home in your terminal{" "}
              <ArrowUpRight size={13} />
            </button>
          </footer>
        </main>
      </div>
      {notice && (
        <div className="sw-toast" role="status">
          <Check size={16} />
          {notice}
        </div>
      )}
      <dialog
        ref={dialog}
        className="sw-dialog"
        onCancel={() => setModal(null)}
        onClick={(e) => {
          if (e.target === dialog.current) setModal(null);
        }}
      >
        <div className="sw-dialog-head">
          <span>
            {modal === "terminal"
              ? "A workspace, two ways in."
              : modal === "connect"
                ? "Connect your local agent."
                : "Find your next session."}
          </span>
          <button aria-label="Close dialog" onClick={() => setModal(null)}>
            <X size={19} />
          </button>
        </div>
        {modal === "connect" && (
          <div className="sw-dialog-body">
            <span className="sw-status">
              {connected ? "Agent connected" : "Agent offline"}
            </span>
            <p>
              Sentinel’s agent runs on your computer, where your files live. The
              website connects to it locally.
            </p>
            <ol>
              <li>Open the Sentinel repository in a terminal.</li>
              <li>
                Install the Python dependencies and start your local Ollama
                model.
              </li>
              <li>Start the API from the core directory:</li>
            </ol>
            <code>
              cd sentinel-core
              <br />
              poetry install
              <br />
              poetry run python -m sentinel_core.api.main
            </code>
            <p className="sw-note">
              File type rules need no model. For Local AI, the default model is qwen3:4b. Download it with{" "}
              <b>ollama pull qwen3:4b</b>. Start only one API process per task
              database. This developer preview requires terminal setup.
            </p>
            <button
              className="sw-primary"
              onClick={async () => {
                await refresh();
                setNotice(
                  "Connection check complete. See agent status in the sidebar.",
                );
              }}
            >
              Check connection <ArrowRight size={15} />
            </button>
          </div>
        )}
        {modal === "terminal" && (
          <div className="sw-dialog-body">
            <Terminal size={28} />
            <p>
              Same local agent. Same review rules. A focused interface for
              people who prefer a keyboard.
            </p>
            <div className="sw-command">
              <code>poetry run sentinel-shell</code>
              <button
                aria-label="Copy terminal command"
                onClick={() => void copy("poetry run sentinel-shell")}
              >
                <Copy size={16} />
              </button>
            </div>
            <dl>
              <dt>/folder &quot;/your/folder&quot;</dt>
              <dd>Set your working folder</dd>
              <dt>Organize my project documents</dt>
              <dd>Describe the result you want</dd>
              <dt>/review</dt>
              <dd>Inspect every proposed change</dd>
              <dt>/apply 1,3</dt>
              <dd>Confirm selected changes by typing APPLY</dd>
            </dl>
            <p className="sw-note">
              Run from sentinel-core after poetry install. The local API must
              already be running.
            </p>
          </div>
        )}
        {modal === "search" && (
          <div className="sw-dialog-body">
            <div className="sw-filter">
              <Search size={17} />
              <input
                autoFocus
                aria-label="Find session"
                placeholder="Search session history…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <button
              className="sw-command-result"
              onClick={() => {
                newSession();
                setModal(null);
              }}
            >
              <Plus size={17} /> Start a new session <ArrowRight size={14} />
            </button>
            <button
              className="sw-command-result"
              onClick={() => {
                setModal("terminal");
              }}
            >
              <Terminal size={17} /> Open terminal guide{" "}
              <ArrowRight size={14} />
            </button>
            {sessions
              .filter((item) =>
                item.summary.toLowerCase().includes(search.toLowerCase()),
              )
              .map((item) => (
                <button
                  className="sw-command-result"
                  key={item.task_id}
                  onClick={() => {
                    openSession(item);
                    setModal(null);
                  }}
                >
                  <History size={16} />
                  {item.summary}
                </button>
              ))}
          </div>
        )}
      </dialog>
      <dialog
        ref={confirmation}
        className="sw-confirm-backdrop"
        onCancel={() => setConfirming(false)}
      >
        {confirming && (
          <section
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="confirm-title"
            className="sw-confirm"
          >
            <ShieldCheck size={28} />
            <h2 id="confirm-title">Apply {selected.length} selected {selected.length === 1 ? "change" : "changes"}?</h2>
            <p>
              {active?.demo
                ? "This sample simulates the selected changes. Your files will not be touched."
                : "Sentinel will apply only the changes you selected. Deletions go to system Trash. Automatic undo is not available in this preview."}
            </p>
            <ul>
              {selected.map((index) => (
                <li key={index}>
                  {basename(actions[index]?.source_path)}{" "}
                  <ArrowRight size={12} />{" "}
                  {actions[index]?.type === "delete"
                    ? "System Trash"
                    : basename(actions[index]?.destination_path)}
                </li>
              ))}
            </ul>
            <div>
              <button
                autoFocus
                className="sw-text-button"
                onClick={() => setConfirming(false)}
              >
                Keep reviewing
              </button>
              <button
                className="sw-primary"
                onClick={() => {
                  setConfirming(false);
                  void apply();
                }}
              >
                {active?.demo
                  ? "Apply sample changes"
                  : "Apply selected changes"}
                <Check size={15} />
              </button>
            </div>
          </section>
        )}
      </dialog>
    </div>
  );
}
