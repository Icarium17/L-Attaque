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
      {!hideMenu && (<header className="fixed top-0 left-0 right-0 z-50">
        <nav className="bg-gray-800 p-3 rounded-lg shadow-lg">
          <ul className="flex space-x-6 justify-center"> 
            {/* Accueil */}
            <li>
              <NavLink
                to="/"
                className={({isActive}) =>
                  isActive
                    ? 'px-4 py-2 rounded-lg bg-blue-600 text-white'
                    : 'px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white'
                } 
              >
                Accueil
              </NavLink>
            </li>

            {/* Autres Onglets si connecté */}
            {session ? (
              <>
                <li>
                  <NavLink
                    to="/lobby"
                    className={({isActive}) =>
                      isActive
                        ? 'px-4 py-2 rounded-lg bg-blue-600 text-white'
                        : 'px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white'
                    }
                  >
                    Lobby
                  </NavLink>
                </li>
                <li>
                  <NavLink
                    to="/game"
                    className={({isActive}) =>
                      isActive
                        ? 'px-4 py-2 rounded-lg bg-blue-600 text-white'
                        : 'px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white'
                    }
                  >
                    Jeu
                  </NavLink>
                </li>
                <li>
                  <NavLink
                    to="/news"
                    className={({isActive}) =>
                      isActive
                        ? 'px-4 py-2 rounded-lg bg-blue-600 text-white'
                        : 'px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white'
                    }
                  >
                    News
                  </NavLink>
                </li>
              </>
            ) : null}
          </ul>
        </nav>     
      </header>
    )}

      <main className="container flex items-center justify-center flex-1 pt-24">
        {children}
      </main>

      <footer>
      </footer>
    </div>
  );
}
