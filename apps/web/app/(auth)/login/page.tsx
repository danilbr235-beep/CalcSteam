export default function LoginPage() {
  return (
    <main className="mx-auto mt-24 max-w-md rounded-xl bg-white p-6 shadow">
      <h1 className="mb-4 text-xl font-semibold">CalcSteam Admin Login</h1>
      <form className="space-y-3">
        <input className="w-full rounded border p-2" placeholder="Email" />
        <input className="w-full rounded border p-2" placeholder="Password" type="password" />
        <button className="w-full rounded bg-slate-900 p-2 text-white">Sign In</button>
      </form>
    </main>
  );
}
