import { apiClient, ApiError } from '../client';
import { CHAT_USES_MOCK, chatService } from '../chat_service';

jest.mock('../client', () => ({
  ...jest.requireActual('../client'),
  apiClient: { post: jest.fn() },
}));

const mockPost = apiClient.post as jest.Mock;

describe('chatService (live POST /chat)', () => {
  beforeEach(() => jest.clearAllMocks());

  it('uses the live endpoint unless EXPO_PUBLIC_CHAT_MOCK is set', () => {
    expect(CHAT_USES_MOCK).toBe(false);
  });

  it('posts the question and returns the answer as a text bubble', async () => {
    mockPost.mockResolvedValue({ data: { answer: 'Okay so, real talk: fewer symptom days lately.', kind: 'answer' } });

    const reply = await chatService.createSession().send('Have my symptoms improved?');

    expect(mockPost).toHaveBeenCalledWith('/chat', { question: 'Have my symptoms improved?' }, { timeout: 45000 });
    expect(reply).toEqual({
      kind: 'answer',
      blocks: [{ type: 'text', text: 'Okay so, real talk: fewer symptom days lately.' }],
    });
  });

  it('keeps refused replies as plain text', async () => {
    mockPost.mockResolvedValue({ data: { answer: 'I can’t say whether that food is a trigger.', kind: 'refused' } });

    const reply = await chatService.createSession().send('Is dairy my trigger?');

    expect(reply.kind).toBe('refused');
    expect(reply.blocks).toEqual([{ type: 'text', text: 'I can’t say whether that food is a trigger.' }]);
  });

  it('shows emergency replies in the safety banner with the backend text', async () => {
    mockPost.mockResolvedValue({ data: { answer: 'Please call 911 now.', kind: 'emergency' } });

    const reply = await chatService.createSession().send('I can’t breathe');

    expect(reply.kind).toBe('emergency');
    expect(reply.blocks).toEqual([
      {
        type: 'card',
        card: expect.objectContaining({ type: 'safety', body: 'Please call 911 now.', phoneNumber: '911' }),
      },
    ]);
  });

  it.each([
    [{ response: { status: 401 } }, 'Your session has expired. Sign in again to keep chatting.'],
    [{ response: { status: 422 } }, 'That message is too long. Try asking in fewer words.'],
    [{ response: { status: 502, data: { detail: 'Chatbot service is unavailable' } } }, 'Sorry, I couldn’t answer just now. Please try again in a moment.'],
    [{ message: 'Network Error' }, 'I can’t reach Remetra right now. Check your connection and try again.'],
  ])('turns %j into a readable error', async (error, message) => {
    mockPost.mockRejectedValue(error);

    const sent = chatService.createSession().send('hi');

    await expect(sent).rejects.toBeInstanceOf(ApiError);
    await expect(sent).rejects.toThrow(message);
  });
});
