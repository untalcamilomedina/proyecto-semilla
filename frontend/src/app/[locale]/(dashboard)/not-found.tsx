export default function DashboardNotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <h2 className="text-2xl font-bold">404</h2>
      <p className="text-muted-foreground">This page does not exist</p>
      <a href="/dashboard" className="text-primary underline">
        Back to Dashboard
      </a>
    </div>
  );
}
