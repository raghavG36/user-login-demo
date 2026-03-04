import { createContext, useCallback, useContext, useState } from 'react'

const ActionsContext = createContext(null)

export function ActionsProvider({ children }) {
  const [actions, setActions] = useState([])

  const addAction = useCallback((action) => {
    setActions((prev) => [...prev, action])
  }, [])

  const value = { actions, addAction }

  return <ActionsContext.Provider value={value}>{children}</ActionsContext.Provider>
}

export function useActions() {
  const ctx = useContext(ActionsContext)
  if (!ctx) throw new Error('useActions must be used within ActionsProvider')
  return ctx
}
