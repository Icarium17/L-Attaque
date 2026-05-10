import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import Notification from "../components/notification.jsx";
import backgroundadmin from "../assets/images/background-admin.png";

export default function Admin() {
  const [session, setSession] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authorized, setAuthorized] = useState(false);

  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newIsAdmin, setNewIsAdmin] = useState(false);
  const [createError, setCreateError] = useState("");

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

    fetch("/api/admin.php", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.redirected ? navigate("/lobby") : res.json())
      .then((data) => {
        if (!data) return;
        if (data.result && data.result.users) {
          setUsers(data.result.users);
        }
        setAuthorized(true);
        setLoading(false);
      })
      .catch(() => {
        navigate("/lobby");
      });
  }, [session, navigate]);

  function deleteUser(id) {
    if (!confirm("Supprimer cet utilisateur ?")) return;

    const formData = new FormData();
    formData.append("action", "delete_user");
    formData.append("key", session.key);
    formData.append("user_id", id);

    fetch("/api/admin.php", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setUsers(users.filter((u) => u._id != id));
        }
      });
  }

  function createUser(e) {
    e.preventDefault();
    setCreateError("");

    if (!newUsername || !newPassword) {
      setCreateError("Champs manquants");
      return;
    }

    const formData = new FormData();
    formData.append("action", "create_user");
    formData.append("key", session.key);
    formData.append("username", newUsername);
    formData.append("password", newPassword);
    formData.append("is_admin", newIsAdmin ? "1" : "0");

    fetch("/api/admin.php", { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setNewUsername("");
          setNewPassword("");
          setNewIsAdmin(false);
          setCreateError("");
          // refresh la liste
          const fd = new FormData();
          fd.append("action", "get_active_users");
          fd.append("key", session.key);
          fetch("/api/admin.php",
             { method: "POST", body: fd })
            .then((r) => r.json())
            .then((d) => d.result?.users && setUsers(d.result.users));
        } else {
          setCreateError(data.result?.error || "Erreur lors de la création");
        }
      });
  }

  if (!authorized) return null;

  return (
    <MainLayout
      title="Administration - L'Attaque"
      background={backgroundadmin}
      session={session}
      hideMenu={true}
    >
      <div className="absolute top-[25%] left-1/2 -translate-x-1/2 w-[70%]">
        <div className="bg-gray-950/70 border-2 border-yellow-600/60 rounded-lg p-6">
          <h1 className="text-center text-yellow-400 text-4xl mb-6">
            Gestion des utilisateurs
          </h1>

          <form onSubmit={createUser} className="flex gap-3 items-center mb-4 text-white">
            <input
              type="text"
              placeholder="Nom d'utilisateur"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              className="px-2 py-1 rounded bg-gray-800 border border-yellow-700/50"
            />
            <input
              type="password"
              placeholder="Mot de passe"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="px-2 py-1 rounded bg-gray-800 border border-yellow-700/50"
            />
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={newIsAdmin}
                onChange={(e) => setNewIsAdmin(e.target.checked)}
              />
              Droits d'administration
            </label>
            <button type="submit" className="relative ml-10 px-10 py-1 bg-green-800 hover:bg-yellow-600 rounded">
              CREER
              {createError && (
                <div
                  style={{
                    position: "absolute",
                    left: "100%",
                    top: "50%",
                    marginLeft: "16px",
                    transform: "translateY(-50%) scale(0.7)",
                    transformOrigin: "left center",
                    whiteSpace: "nowrap",
                  }}
                >
                  <Notification
                    variant="error"
                    message={createError}
                    onClose={() => setCreateError("")}
                  />
                </div>
              )}
            </button>
          </form>

          <table className="w-full text-center text-lg">
            <tbody>
              <tr className="bg-blue-900/80 text-white">
                <th className="py-3 px-4">ID</th>
                <th className="py-3 px-4">Connexion</th>
                <th className="py-3 px-4">Login</th>
                <th className="py-3 px-4">Droits</th>
                <th className="py-3 px-4">Action</th>
              </tr>

              {loading ? (
                <tr>
                  <td
                    colSpan={5}
                    className="py-10 text-center text-gray-400 italic"
                  > 
                  Chargement des données...
                  </td>
                </tr>
              ) : users.length > 0 ? (
                users
                  .sort((a, b) => a._id - b._id)
                  .map((user) => (
                    <tr
                      key={user._id}
                      className="border-t border-yellow-700/40 text-gray-100"
                    >
                      <td className="py-3 px-4">{user._id}</td>
                      <td
                        className={`py-3 px-4 text-center align-middle ${
                          user.connected
                            ? "text-green-500 text-4xl"
                            : "text-red-500 text-4xl"
                        }`}
                      >
                        ●
                      </td>
                      <td className="py-3 px-4">{user.username}</td>
                      <td className="py-3 px-4">
                        {user.rights == "Admin" ? (
                          <span className="text-yellow-400 font-semibold">Admin</span>
                        ) : (
                          <span className="text-gray-400">User</span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => deleteUser(user._id)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))
              ) : (
                <tr>
                  <td
                    colSpan={5}
                    className="py-10 text-center text-gray-400 italic"
                  >
                    Aucune donnée retournée
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* BOUTON RETOUR */}
      <div className="absolute top-[93%] left-1/2 -translate-x-1/2 w-[12%] flex flex-col gap-[3%] z-10">
        <Button
          variant="danger"
          onClick={() => navigate("/lobby")}
          className="w-full"
        >
          RETOUR
        </Button>
      </div>
    </MainLayout>
  );
}