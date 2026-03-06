import { NavLink } from "react-router";

export default function MainLayout({ children, background, session, hideMenu }) {

  return (
    <div
      className="h-screen overflow-hidden bg-cover bg-center bg-no-repeat flex flex-col"
      style={{
        backgroundImage: 'url(' + background + ')',
        backgroundSize: 'cover'
      }}
    >
      {/* Navbar : visible seulement si hideMenu=false et si la session existe */}
      {!hideMenu && session && (
        <header className="fixed top-0 left-0 right-0 z-50">
          <nav
            className="p-3 shadow-lg"
            style={{
              background: 'linear-gradient(to bottom, rgba(20,15,10,0.95), rgba(30,25,15,0.9))',
              borderBottom: '1px solid rgba(212,164,74,0.3)',
            }}
          >
            <ul className="flex space-x-6 justify-center items-center">
              {/* Accueil */}
              <li>
                <NavLink
                  to="/"
                  className={({ isActive }) =>
                    isActive
                      ? 'px-4 py-2 rounded-lg text-amber-300 font-semibold'
                      : 'px-4 py-2 rounded-lg text-gray-400 hover:text-amber-200 transition-colors'
                  }
                  style={({ isActive }) =>
                    isActive
                      ? { background: 'rgba(212,164,74,0.15)', border: '1px solid rgba(212,164,74,0.3)' }
                      : {}
                  }
                >
                  Accueil
                </NavLink>
              </li>

              {/* Lobby */}
              <li>
                <NavLink
                  to="/lobby"
                  className={({ isActive }) =>
                    isActive
                      ? 'px-4 py-2 rounded-lg text-amber-300 font-semibold'
                      : 'px-4 py-2 rounded-lg text-gray-400 hover:text-amber-200 transition-colors'
                  }
                  style={({ isActive }) =>
                    isActive
                      ? { background: 'rgba(212,164,74,0.15)', border: '1px solid rgba(212,164,74,0.3)' }
                      : {}
                  }
                >
                  Lobby
                </NavLink>
              </li>

              {/* Jeu si une partie est en cours */}
              <li>
                <NavLink
                  to="/game"
                  className={({ isActive }) =>
                    isActive
                      ? 'px-4 py-2 rounded-lg text-amber-300 font-semibold'
                      : 'px-4 py-2 rounded-lg text-gray-400 hover:text-amber-200 transition-colors'
                  }
                  style={({ isActive }) =>
                    isActive
                      ? { background: 'rgba(212,164,74,0.15)', border: '1px solid rgba(212,164,74,0.3)' }
                      : {}
                  }
                >
                  Jeu
                </NavLink>
              </li>
            </ul>
          </nav>
        </header>
      )}

      <main className={"flex items-center justify-center flex-1" + (!hideMenu && session ? " pt-16" : "")}>
        {children}
      </main>

      <footer>
      </footer>
    </div>
  );
}
