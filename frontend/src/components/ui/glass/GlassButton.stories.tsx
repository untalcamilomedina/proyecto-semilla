import type { Meta, StoryObj } from '@storybook/react';
import { GlassButton } from './GlassButton';

/**
 * The GlassButton is the core interactive primitive of our Design System.
 * It strictly adheres to JSON-provided semantic tokens to automatically
 * support light/dark modes and custom tenant themes.
 */
const meta = {
  title: 'UI/Glass/GlassButton',
  component: GlassButton,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger'],
      description: 'The visual style variant mapped to semantic tokens.',
    },
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
      description: 'Button size and touch target dimensions.',
    },
    isLoading: {
      control: 'boolean',
      description: 'Loading state that disables the button and shows a spinner.',
    },
    disabled: {
      control: 'boolean',
    },
    children: {
      control: 'text',
    },
  },
} satisfies Meta<typeof GlassButton>;

export default meta;
type Story = StoryObj<typeof meta>;

// --- Stories ---

export const Primary: Story = {
  args: {
    variant: 'primary',
    size: 'md',
    children: 'Save Changes',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    size: 'md',
    children: 'Cancel',
  },
};

export const Danger: Story = {
  args: {
    variant: 'danger',
    size: 'md',
    children: 'Delete Account',
  },
};

export const LoadingState: Story = {
  args: {
    variant: 'primary',
    size: 'md',
    isLoading: true,
    children: 'Processing...',
  },
};

export const SmallSize: Story = {
  args: {
    variant: 'primary',
    size: 'sm',
    children: 'Click me',
  },
};

export const LargeSize: Story = {
  args: {
    variant: 'primary',
    size: 'lg',
    children: 'Get Started Now',
  },
};
