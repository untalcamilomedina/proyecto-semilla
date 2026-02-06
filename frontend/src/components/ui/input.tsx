import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
    extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

/**
 * Form input field with integrated label and error handling.
 * 
 * @vibe Form & Data Integrity - Consistent styling for data entry.
 * Supports `label` and `error` props for automatic layout.
 */
const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, type, label, error, id, ...props }, ref) => {
        const inputId = id || React.useId();

        return (
            <div className="space-y-1.5">
                {label && (
                    <label
                        htmlFor={inputId}
                        className="text-sm font-medium text-foreground"
                    >
                        {label}
                    </label>
                )}
                <input
                    type={type}
                    id={inputId}
                    className={cn(
                        "flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors",
                        "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
                        "placeholder:text-muted-foreground",
                        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:border-ring",
                        "disabled:cursor-not-allowed disabled:opacity-50",
                        error && "border-destructive focus-visible:ring-destructive",
                        className
                    )}
                    ref={ref}
                    {...props}
                />
                {error && (
                    <p className="text-sm text-error-text">{error}</p>
                )}
            </div>
        );
    }
);
Input.displayName = "Input";

export { Input };
