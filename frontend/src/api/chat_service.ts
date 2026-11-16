import { apiClient, ApiError } from './client';
import { createMockChatEngine, SAFETY_CARD } from './mock_chat_engine';
import type { ChatReply } from '../types/chat';

// Ask Remetra talks to POST /chat. Set EXPO_PUBLIC_CHAT_MOCK=true to use the local mock,
// which walks through every Ask Remetra design (cards, drafts, recipes) with demo data.
export const CHAT_USES_MOCK = process.env.EXPO_PUBLIC_CHAT_MOCK === 'true';
const MOCK_REPLY_DELAY_MS = 700;
const CHAT_TIMEOUT_MS = 45000;

const ERROR_MESSAGES = {
  unauthorized: 'Your session has expired. Sign in again to keep chatting.',
  tooLong: 'That message is too long. Try asking in fewer words.',
  offline: 'I can’t reach Remetra right now. Check your connection and try again.',
  unavailable: 'Sorry, I couldn’t answer just now. Please try again in a moment.',
};

interface ChatApiResponse {
  answer: string;
  kind: 'answer' | 'emergency' | 'refused';
}

export interface ChatSession {
  send: (message: string) => Promise<ChatReply>;
}

export function toChatReply(data: ChatApiResponse): ChatReply {
  if (data.kind === 'emergency') {
    return { kind: 'emergency', blocks: [{ type: 'card', card: { ...SAFETY_CARD, body: data.answer } }] };
  }
  return { kind: data.kind, blocks: [{ type: 'text', text: data.answer }] };
}

function toChatError(err: any): ApiError {
  const status: number | undefined = err.response?.status;
  if (status === 401 || status === 403) return new ApiError(ERROR_MESSAGES.unauthorized);
  if (status === 422) return new ApiError(ERROR_MESSAGES.tooLong);
  if (!err.response) return new ApiError(ERROR_MESSAGES.offline);
  return new ApiError(ERROR_MESSAGES.unavailable);
}

function createApiSession(): ChatSession {
  return {
    async send(message) {
      try {
        const { data } = await apiClient.post<ChatApiResponse>(
          '/chat',
          { question: message },
          { timeout: CHAT_TIMEOUT_MS }
        );
        return toChatReply(data);
      } catch (err: any) {
        throw toChatError(err);
      }
    },
  };
}

function createMockSession(): ChatSession {
  const engine = createMockChatEngine();
  return {
    send: (message) =>
      new Promise((resolve) => setTimeout(() => resolve(engine.reply(message)), MOCK_REPLY_DELAY_MS)),
  };
}

export const chatService = {
  createSession(): ChatSession {
    return CHAT_USES_MOCK ? createMockSession() : createApiSession();
  },
};
