import { useActions } from '../context/ActionsContext'

function formatOp(operation, a, b, result) {
  const opSymbol = { add: '+', subtract: '-', multiply: '×', divide: '÷' }[operation] || operation
  return `${a} ${opSymbol} ${b} = ${result}`
}

export default function ActionsPerformed() {
  const { actions } = useActions()

  return (
    <div className="card">
      <h1 className="page-title">Actions Performed</h1>
      <p style={{ color: 'var(--muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
        Calculator operations from this session (newest first).
      </p>
      {actions.length === 0 ? (
        <p className="empty-state">No actions yet. Use the Calculator to perform operations.</p>
      ) : (
        <div>
          {[...actions].reverse().map((action, i) => (
            <div key={action.at + i} className="action-row">
              <span className="action-op">
                {formatOp(action.operation, action.a, action.b, action.result)}
              </span>
              <span className="action-result">{action.result}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
