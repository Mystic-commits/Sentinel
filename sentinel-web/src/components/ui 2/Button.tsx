/**
 * Button Component
 * 
 * Reference implementation for the Sentinel design system.
 * Demonstrates variants, sizes, states, and best practices.
 */

import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
    loading?: boolean;
    icon?: React.ReactNode;
    children: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
    primary: `
    bg-gradient-to-r from-primary to-neon-blue
    hover:from-neon-cyan hover:to-primary
    border border-transparent
    text-black font-bold tracking-wide
    shadow-neon-cyan hover:shadow-glow-md
    transition-all duration-300
    transform hover:-translate-y-0.5
  `,
    secondary: `
    glass-button
    text-slate-300 hover:text-white
    hover:border-primary/50 hover:shadow-glow-sm
    transition-all duration-300
  `,
    ghost: `
    text-slate-400 hover:text-primary 
    hover:bg-primary/5
    transition-colors duration-200
  `,
    danger: `
    bg-red-500/10 border border-red-500/50
    text-red-400 hover:text-white
    hover:bg-red-500 hover:shadow-[0_0_15px_rgba(239,68,68,0.4)]
    transition-all duration-300
  `,
};

const sizeClasses: Record<ButtonSize, string> = {
    sm: 'px-3 py-1.5 text-xs rounded-md',
    md: 'px-5 py-2.5 text-sm rounded-lg',
    lg: 'px-8 py-4 text-base rounded-xl',
};

export function Button({
    variant = 'primary',
    size = 'md',
    loading = false,
    icon,
    children,
    disabled,
    className = '',
    ...props
}: ButtonProps) {
    return (
        <button
            className={`
        font-medium
        inline-flex items-center justify-center gap-2
        disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none
        focus:outline-none focus:ring-2 focus:ring-primary/50
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
            disabled={disabled || loading}
            {...props}
        >
            {loading && (
                <svg
                    className="animate-spin h-4 w-4"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                >
                    <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                    />
                    <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                </svg>
            )}
            {!loading && icon}
            {children}
        </button>
    );
}
