import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';

const Alert = ({ type = 'info', title, message, onClose }) => {
  const alertConfig = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: CheckCircle,
      textColor: 'text-green-800',
      titleColor: 'text-green-900',
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: XCircle,
      textColor: 'text-red-800',
      titleColor: 'text-red-900',
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      icon: AlertCircle,
      textColor: 'text-yellow-800',
      titleColor: 'text-yellow-900',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: AlertCircle,
      textColor: 'text-blue-800',
      titleColor: 'text-blue-900',
    },
  };

  const config = alertConfig[type];
  const Icon = config.icon;

  return (
    <div className={`${config.bg} border ${config.border} rounded-lg p-4 flex items-start gap-4`}>
      <Icon className={`w-5 h-5 ${config.textColor} flex-shrink-0 mt-0.5`} />
      <div className="flex-1">
        {title && <h3 className={`font-semibold ${config.titleColor}`}>{title}</h3>}
        {message && <p className={`text-sm ${config.textColor}`}>{message}</p>}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className={`text-sm font-medium ${config.textColor} hover:opacity-75`}
          aria-label="Close alert"
        >
          X
        </button>
      )}
    </div>
  );
};

export default Alert;
