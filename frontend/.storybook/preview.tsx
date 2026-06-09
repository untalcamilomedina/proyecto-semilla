import type { Preview } from '@storybook/react';
import React from 'react';
import { Providers } from '../src/components/providers';
import '../src/app/globals.css';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    nextjs: {
      appDirectory: true,
    },
  },
  decorators: [
    (Story) => (
      <Providers locale="es" messages={{}}>
        <div className="font-body text-foreground">
          <Story />
        </div>
      </Providers>
    ),
  ],
};

export default preview;