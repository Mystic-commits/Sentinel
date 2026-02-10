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
        bg-white text-black font-semibold
        hover:bg-neutral-200
        border border-transparent
        transition-colors duration-150
    `,
    secondary: `
        bg-surface-2 text-txt-primary
        border border-edge
        hover:bg-surface-3 hover:border-edge-hover
        transition-colors duration-150
    `,
    ghost: `
        text-txt-secondary hover:text-txt-primary
        hover:bg-surface-2
        transition-colors duration-150
    `,
    danger: `
        bg-red-600 text-white font-semibold
        border border-transparent
        hover:bg-red-500
        transition-colors duration-150
    `,
};

const sizeClasses: Record<ButtonSize, string> = {
    sm: 'h-8 px-3 text-[13px] rounded-lg gap-1.5',
    md: 'h-10 px-5 text-[14px] rounded-lg gap-2',
    lg: 'h-12 px-8 text-[15px] rounded-xl gap-2.5',
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
                inline-flex items-center justify-center
                disabled:opacity-40 disabled:cursor-not-allowed
                focus:outline-none focus-visible:ring-2 focus-visible:ring-white/20
                ${variantClasses[variant]}
                ${sizeClasses[size]}
                ${className}
            `}
            disabled={disabled || loading}
            {...props}
        >
            {loading && (
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
            )}
            {!loading && icon}
            {children}
        </button>
    );
}
