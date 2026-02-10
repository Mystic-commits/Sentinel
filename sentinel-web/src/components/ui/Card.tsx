import React from 'react';

type CardVariant = 'standard' | 'elevated' | 'interactive';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: CardVariant;
    children: React.ReactNode;
}

const variantClasses: Record<CardVariant, string> = {
    standard: `
        bg-surface-1 border border-edge
    `,
    elevated: `
        bg-surface-2 border border-edge
    `,
    interactive: `
        bg-surface-1 border border-edge
        hover:border-edge-hover hover:bg-surface-2
        transition-all duration-150
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
                <h3 className="text-[16px] font-semibold text-txt-primary">{title}</h3>
                {subtitle && <p className="text-[14px] text-txt-secondary mt-1">{subtitle}</p>}
            </div>
            {action && <div>{action}</div>}
        </div>
    );
}

export function CardContent({ children, className = '' }: { children: React.ReactNode; className?: string }) {
    return <div className={`text-txt-primary ${className}`}>{children}</div>;
}

export function CardFooter({ children, className = '' }: { children: React.ReactNode; className?: string }) {
    return <div className={`mt-4 pt-4 border-t border-edge ${className}`}>{children}</div>;
}
