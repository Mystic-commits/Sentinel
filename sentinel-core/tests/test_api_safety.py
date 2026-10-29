import pytest
from fastapi.testclient import TestClient
from sentinel_core.api.main import app
from sentinel_core.api.memory import save_task, task_store
from sentinel_core.models.planner import PlanSchema, PlanAction
from sentinel_core.models.enums import TaskState


@pytest.fixture
def client():
    task_store.clear()
    with TestClient(app, base_url='http://127.0.0.1') as client:
        yield client
    task_store.clear()


def seed(tmp_path):
    actions=[]
    for name in ['approved', 'rejected']:
        source=tmp_path/name; source.write_text(name)
        actions.append(PlanAction(type='move', source_path=str(source), destination_path=str(tmp_path/'organized'/name), reason='test', confidence=1))
    plan=PlanSchema(task_id='approval', scope_path=str(tmp_path), actions=actions, folders_to_create=[str(tmp_path/'unapproved-folder')], summary='test')
    save_task('approval', {'plan':plan, 'state':TaskState.REVIEW})


def test_approval_required(client,tmp_path):
    seed(tmp_path)
    assert client.post('/api/execute',json={'task_id':'approval'}).status_code == 422
    assert client.post('/api/execute',json={'task_id':'approval','approved_actions':[]}).status_code == 422
    assert (tmp_path/'approved').exists()


def test_only_selected_actions_execute_and_no_replay(client,tmp_path):
    seed(tmp_path)
    payload={'task_id':'approval','approved_actions':[0]}
    assert client.post('/api/execute',json=payload).status_code == 200
    assert (tmp_path/'organized'/'approved').read_text() == 'approved'
    assert (tmp_path/'rejected').exists()
    assert not (tmp_path/'unapproved-folder').exists()
    assert client.post('/api/execute',json=payload).status_code == 409


@pytest.mark.parametrize('indices', [[-1],[2],[0,0]])
def test_invalid_selection(client,tmp_path,indices):
    seed(tmp_path)
    assert client.post('/api/execute',json={'task_id':'approval','approved_actions':indices}).status_code == 422
    assert (tmp_path/'approved').exists()


def test_external_origin_blocked(client):
    assert client.get('/api/tasks',headers={'Origin':'https://evil.example'}).status_code == 403
    assert client.get('/api/tasks',headers={'Host':'evil.example'}).status_code == 403
    assert client.get('/api/tasks',headers={'Origin':'http://localhost:3000'}).status_code == 200


def test_websocket_external_origin_blocked(client):
    from starlette.websockets import WebSocketDisconnect
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/ws/events', headers={'Origin':'https://evil.example'}):
            pass


def test_scan_runs_without_developer_directory(client,tmp_path):
    (tmp_path/'sample.txt').write_text('sample')
    assert client.post('/api/scan',json={'path':str(tmp_path),'max_depth':1}).status_code == 200
