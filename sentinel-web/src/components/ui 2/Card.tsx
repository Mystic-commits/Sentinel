/**
 * Card Component
 * 
 * Reference implementation for card/panel layouts.
 * Demonstrates standard, elevated, and interactive variants.
 */

import React from 'react';

type CardVariant = 'standard' | 'elevated' | 'interactive';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: CardVariant;
    children: React.ReactNode;
}

const variantClasses: Record<CardVariant, string> = {
    standard: `
    bg-background-elevated
    border border-slate-800
    shadow-card
  `,
    elevated: `
    bg-background-panel
    border border-slate-700
    shadow-card-lg
  `,
    interactive: `
    bg-background-elevated
    border border-slate-800
    hover:border-primary/30
    hover:shadow-glow-sm
    transition-all duration-200
    cursor-pointer
  `,
};

export function Card({
    variant = 'standard',
    className = '',
    children,
    ...props
}: CardProps) {
    return (
        <div
            className={`
        rounded-xl p-6
        ${variantClasses[variant]}
        ${className}
      `}
            {...props}
        >
            {children}
        </div>
    );
}

interface CardHeaderProps {
    title: string;
    subtitle?: string;
    action?: React.ReactNode;
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
    return (
        <div className="flex items-start justify-between mb-4">
            <div>
                <h3 className="text-lg font-semibold text-slate-50">{title}</h3>
                {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
            </div>
            {action && <div>{action}</div>}
        </div>
    );
}

export function CardContent({ children, className = '' }: { children: React.ReactNode; className?: string }) {
    return <div className={`text-slate-200 ${className}`}>{children}</div>;
}

export function CardFooter({ children, className = '' }: { children: React.ReactNode; className?: string }) {
    return <div className={`mt-4 pt-4 border-t border-slate-800 ${className}`}>{children}</div>;
}
