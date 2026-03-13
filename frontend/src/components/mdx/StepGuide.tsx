/**
 * Step-by-step guide component for MDX content.
 * Perfect for tutorials and onboarding flows.
 *
 * Usage in MDX:
 * <StepGuide steps={[
 *   { title: "Install", content: "Run npm install..." },
 *   { title: "Configure", content: "Edit next.config..." },
 * ]} />
 */
'use client';

interface Step {
  title: string;
  content: string;
}

interface StepGuideProps {
  steps: Step[];
}

export function StepGuide({ steps }: StepGuideProps) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="my-6 space-y-4" role="list" aria-label="Step-by-step guide">
      {steps.map((step, idx) => (
        <div
          key={step.title}
          className="flex gap-4 items-start"
          role="listitem"
        >
          {/* Step number */}
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-sky-400/20 border border-sky-400/40 flex items-center justify-center text-sky-400 font-semibold text-sm">
            {idx + 1}
          </div>

          {/* Step content */}
          <div className="flex-1 glass-card p-4">
            <h4 className="font-semibold text-white/90 mb-1">{step.title}</h4>
            <p className="text-sm text-white/60 leading-relaxed">{step.content}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
