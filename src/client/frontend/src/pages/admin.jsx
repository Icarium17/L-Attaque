import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import backgroundadmin from "../assets/images/background-admin.png";

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

    fetch("/api/admin.php", {
      method: "POST",
      body: formData,
    })
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

          <table className="w-full text-center text-lg">
            <tbody>
              <tr className="bg-blue-900/80 text-white">
                <th className="py-3 px-4">ID</th>
                <th className="py-3 px-4">Connexion</th>
                <th className="py-3 px-4">Login</th>
                <th className="py-3 px-4">Action</th>
              </tr>

              {loading ? (
                <tr>
                  <td
                    colSpan={4}
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
                    colSpan={4}
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