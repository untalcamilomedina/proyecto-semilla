export default function NotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <h2 className="text-2xl font-bold">404</h2>
      <p className="text-muted-foreground">Page not found</p>
      <a href="/dashboard" className="text-primary underline">
        Go to Dashboard
      </a>
    </div>
  );
}
