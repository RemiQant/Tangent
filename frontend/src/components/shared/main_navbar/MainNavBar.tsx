import { IoNotificationsOutline } from "react-icons/io5";
import { IoSettingsOutline } from "react-icons/io5";
import { FiLogOut } from "react-icons/fi";
import { useState } from "react";

function MainNavBar() {
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  return (
    <div className="w-full h-22 bg-linear-to-r from-gray-900 via-gray-800 to-gray-900 border-b border-gray-700 shadow-lg sticky top-0 z-40">
      <div className="flex items-center justify-end h-full px-8 gap-6">

        {/* Notification Icon */}
        <button className="relative p-2 hover:bg-gray-700 rounded-lg transition-colors duration-200 group hover:cursor-pointer animate-fadeIn" style={{animationDelay: '100ms'}}>
          <IoNotificationsOutline className="text-2xl text-gray-400 group-hover:text-white transition-colors" />
          <span className="absolute top-1 right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-semibold">3</span>
        </button>

        {/* Settings Icon */}
        <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors duration-200 group hover:cursor-pointer animate-fadeIn" style={{animationDelay: '200ms'}}>
          <IoSettingsOutline className="text-2xl text-gray-400 group-hover:text-white transition-colors" />
        </button>

        {/* Divider */}
        <div className="w-px h-6 bg-gray-700 animate-fadeIn" style={{animationDelay: '200ms'}}></div>

        {/* Profile Menu */}
        <div className="relative animate-fadeIn" style={{animationDelay: '300ms'}}>
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-3 p-2 hover:bg-gray-700 rounded-lg transition-colors duration-200 hover:cursor-pointer"
          >
            <div className="w-8 h-8 bg-linear-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shrink-0">
              <span className="text-white text-xs font-bold">JD</span>
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-sm font-semibold text-white">John Doe</p>
              <p className="text-xs text-gray-400">Premium</p>
            </div>
          </button>

          {/* Profile Dropdown Menu */}
          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 animate-fadeIn" style={{animationDelay: '0ms'}}>
              <div className="p-4 border-b border-gray-700">
                <p className="text-sm font-semibold text-white">John Doe</p>
                <p className="text-xs text-gray-400">john@example.com</p>
              </div>
              <ul className="py-2">
                <li className="">
                  <button className="w-full text-left px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-gray-700 flex items-center gap-2 transition-colors hover:cursor-pointer">
                    <FiLogOut /> Logout
                  </button>
                </li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MainNavBar;