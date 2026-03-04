import { useState } from 'react'
import * as api from '../api/client'
import { useActions } from '../context/ActionsContext'

const OPS = [
  { value: 'add', label: 'Add' },
  { value: 'subtract', label: 'Subtract' },
  { value: 'multiply', label: 'Multiply' },
  { value: 'divide', label: 'Divide' },
]

export default function Calculator() {
  const [a, setA] = useState('')
  const [b, setB] = useState('')
  const [operation, setOperation] = useState('add')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const { addAction } = useActions()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    const numA = parseFloat(a)
    const numB = parseFloat(b)
    if (Number.isNaN(numA) || Number.isNaN(numB)) {
      setError('Please enter valid numbers')
      return
    }
    setSubmitting(true)
    try {
      const data = await api.calculatorOp(operation, numA, numB)
      setResult(data.result)
      addAction({
        operation: data.operation,
        a: data.a,
        b: data.b,
        result: data.result,
        at: new Date().toISOString(),
      })
    } catch (err) {
      setError(err.data?.detail || err.message || 'Calculation failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="card">
      <h1 className="page-title">Calculator</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="op">Operation</label>
          <select id="op" value={operation} onChange={(e) => setOperation(e.target.value)}>
            {OPS.map((op) => (
              <option key={op.value} value={op.value}>{op.label}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="a">First number</label>
          <input
            id="a"
            type="number"
            step="any"
            value={a}
            onChange={(e) => setA(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="b">Second number</label>
          <input
            id="b"
            type="number"
            step="any"
            value={b}
            onChange={(e) => setB(e.target.value)}
            required
          />
        </div>
        {error && <p className="error-msg">{error}</p>}
        {result !== null && (
          <p className="success-msg">Result: <strong>{result}</strong></p>
        )}
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Calculating...' : 'Calculate'}
        </button>
      </form>
    </div>
  )
}
