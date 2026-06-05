export default function HepPhysicsPage() {
  return (
    <div className="flex h-full w-full flex-col">
      <iframe
        src="http://localhost:3200"
        className="h-full w-full flex-1 border-0"
        title="HEP Physics Dashboard"
        allow="same-origin"
      />
    </div>
  );
}
