import type { Meta, StoryObj } from '@storybook/react';
import { GlassCard } from './GlassCard';

const meta = {
  title: 'UI/Glass/GlassCard',
  component: GlassCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'highlight'],
      description: 'The visual style variant.',
    },
    children: {
      control: 'text',
    },
  },
} satisfies Meta<typeof GlassCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    variant: 'default',
    className: 'p-8 w-96 text-center leading-relaxed text-muted-foreground',
    children: 'This is a standard semantic GlassCard taking responsive values from the JSON theme.',
  },
};

export const HighlightGlow: Story = {
  args: {
    variant: 'highlight',
    className: 'p-8 w-96 text-center leading-relaxed text-primary',
    children: 'This GlassCard uses the primary color semantics from the theme to emit a glow, overriding legacy hardcoded neon values.',
  },
};
