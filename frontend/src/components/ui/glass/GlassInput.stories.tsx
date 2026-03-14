import type { Meta, StoryObj } from '@storybook/react';
import { GlassInput } from './GlassInput';

const meta = {
  title: 'UI/Glass/GlassInput',
  component: GlassInput,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    label: {
      control: 'text',
      description: 'Accessible label above the input.',
    },
    error: {
      control: 'text',
      description: 'Error message that toggles the invalid state ring and border.',
    },
    placeholder: {
      control: 'text',
    },
    disabled: {
      control: 'boolean',
    },
  },
} satisfies Meta<typeof GlassInput>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    label: 'Email Address',
    placeholder: 'name@company.com',
    type: 'email',
  },
};

export const WithError: Story = {
  args: {
    label: 'Password',
    placeholder: 'Enter your password',
    type: 'password',
    error: 'Password must be at least 8 characters long.',
  },
};

export const Disabled: Story = {
  args: {
    label: 'Username',
    placeholder: '@untalcamilomedina',
    disabled: true,
  },
};
