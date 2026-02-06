import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { GlassButton } from "../GlassButton";

describe("GlassButton", () => {
    it("renders children", () => {
        render(<GlassButton>Click me</GlassButton>);
        expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
    });

    it("applies primary variant by default", () => {
        render(<GlassButton>Primary</GlassButton>);
        const btn = screen.getByRole("button");
        expect(btn.className).toContain("bg-neon-bg-strong");
    });

    it("applies secondary variant", () => {
        render(<GlassButton variant="secondary">Secondary</GlassButton>);
        const btn = screen.getByRole("button");
        expect(btn.className).toContain("bg-glass-bg");
    });

    it("applies danger variant", () => {
        render(<GlassButton variant="danger">Danger</GlassButton>);
        const btn = screen.getByRole("button");
        expect(btn.className).toContain("bg-error-bg");
    });

    it("handles click events", async () => {
        const user = userEvent.setup();
        const onClick = vi.fn();
        render(<GlassButton onClick={onClick}>Click</GlassButton>);

        await user.click(screen.getByRole("button"));
        expect(onClick).toHaveBeenCalledOnce();
    });

    it("respects disabled state", async () => {
        const user = userEvent.setup();
        const onClick = vi.fn();
        render(<GlassButton disabled onClick={onClick}>Disabled</GlassButton>);

        const btn = screen.getByRole("button");
        expect(btn).toBeDisabled();
        await user.click(btn);
        expect(onClick).not.toHaveBeenCalled();
    });

    it("merges custom className", () => {
        render(<GlassButton className="custom-class">Custom</GlassButton>);
        expect(screen.getByRole("button").className).toContain("custom-class");
    });
});
