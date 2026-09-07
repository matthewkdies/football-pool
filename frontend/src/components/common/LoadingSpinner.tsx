export function LoadingSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] gap-4 p-8">
      <span className="loading loading-spinner loading-lg text-primary"></span>
      <p className="text-sm font-medium text-base-content/70">{message}</p>
    </div>
  );
}
