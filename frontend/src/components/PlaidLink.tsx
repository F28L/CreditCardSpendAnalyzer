import { useEffect, useState, useCallback } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { apiClient } from '../services/api';

interface PlaidLinkButtonProps {
  onSuccess?: () => void;
  onExit?: () => void;
}

export default function PlaidLinkButton({ onSuccess, onExit }: PlaidLinkButtonProps) {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch link token on mount
  useEffect(() => {
    const createLinkToken = async () => {
      try {
        setLoading(true);
        const response = await apiClient.createLinkToken();
        setLinkToken(response.link_token);
      } catch (err: any) {
        console.error('Error creating link token:', err);
        setError(err.message || 'Failed to initialize Plaid Link');
      } finally {
        setLoading(false);
      }
    };

    createLinkToken();
  }, []);

  const onPlaidSuccess = useCallback(
    async (public_token: string, metadata: any) => {
      try {
        setLoading(true);
        console.log('Plaid Link success:', { public_token, metadata });

        // Exchange public token for access token
        const result = await apiClient.exchangePublicToken(public_token);
        console.log('Token exchange successful:', result);

        // Call the success callback
        if (onSuccess) {
          onSuccess();
        }
      } catch (err: any) {
        console.error('Error exchanging public token:', err);
        setError(err.message || 'Failed to connect bank account');
      } finally {
        setLoading(false);
      }
    },
    [onSuccess]
  );

  const onPlaidExit = useCallback(
    (error: any, metadata: any) => {
      console.log('Plaid Link exit:', { error, metadata });
      if (error) {
        setError(error.display_message || 'Connection cancelled');
      }
      if (onExit) {
        onExit();
      }
    },
    [onExit]
  );

  const config = {
    token: linkToken,
    onSuccess: onPlaidSuccess,
    onExit: onPlaidExit,
  };

  const { open, ready } = usePlaidLink(config);

  // Handle button click
  const handleClick = () => {
    if (ready) {
      setError(null);
      open();
    }
  };

  if (error) {
    return (
      <div className="flex flex-col items-center space-y-2">
        <button
          onClick={handleClick}
          disabled={!ready || loading}
          className="px-4 py-2 rounded-xl bg-wallet-accent-blue/10 text-wallet-accent-blue hover:bg-wallet-accent-blue/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Connecting...' : 'Connect Bank'}
        </button>
        <p className="text-red-400 text-xs">{error}</p>
      </div>
    );
  }

  return (
    <button
      onClick={handleClick}
      disabled={!ready || loading}
      className="px-4 py-2 rounded-xl bg-wallet-accent-blue/10 text-wallet-accent-blue hover:bg-wallet-accent-blue/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {loading ? 'Connecting...' : !ready ? 'Loading...' : 'Connect Bank'}
    </button>
  );
}
