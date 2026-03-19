import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";

export default function Admin() {
  const [session, setSession] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (!key || !username) {
      navigate("/");
    } else {
      setSession({ username, key });
    }
  }, [navigate]);

  useEffect(() => {
    if (!session) return;

    const formData = new FormData();
    formData.append("action", "get_active_users");
    formData.append("key", session.key);

    fetch("/api/admin.php", { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        if (data.result && data.result.users) {
          setUsers(data.result.users);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [session]);

  function deleteUser(id) {
    if (!confirm("Supprimer cet utilisateur ?")) return;

    const formData = new FormData();
    formData.append("action", "delete_user");
    formData.append("key", session.key);
    formData.append("user_id", id);

    fetch("/api/admin.php", { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setUsers(users.filter((u) => u._id != id));
        }
      });
  }

  return (
    <MainLayout title="Admin - L'Attaque" session={session}>
      <div className="max-w-3xl mx-auto p-6 pb-24 overflow-y-auto h-screen">
        <h1 className="text-2xl font-bold mb-6 text-yellow-400">
          Utilisateurs
        </h1>

        {loading ? (
          <p>Chargement...</p>
        ) : users.length == 0 ? (
          <p>Aucun utilisateur.</p>
        ) : (
          <div className="border border-gray-300 rounded mb-6">
            {users
              .sort((a, b) => a._id - b._id)
              .map((user) => (
                <div key={user._id} className="border-b border-gray-300 py-3 px-4 flex gap-8 items-center">
                  <span>{user._id}</span>
                  <span className={user.connected ? "text-green-500" : "text-gray-400"}>●</span>
                  <span className="flex-1">{user.username}</span>
                  <button
                    onClick={() => deleteUser(user._id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Supprimer
                  </button>
                </div>
              ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}