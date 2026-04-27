export function ConfirmButton({ onConfirm, loading, disabled }) {
  return (
    <button
      onClick={onConfirm}
      disabled={loading || disabled}
      className="w-full py-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white text-lg font-semibold rounded-xl transition-colors"
    >
      {loading ? "Confirming..." : "Confirm & close session"}
    </button>
  );
}
