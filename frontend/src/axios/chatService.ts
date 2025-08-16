import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const sendChatMessage = async (sessionId: string, question: string): Promise<string> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      session_id: sessionId,
      question: question,
    });
    
    return response.data.answer;
  } catch (error) {
    console.error("Error sending chat message:", error);
    throw error;
  }
};

// STREAMING CHAT FUNCTION
export const sendChatMessageStream = async (
  sessionId: string, 
  question: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: any) => void
): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        question: question,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('ReadableStream not supported');
    }

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        onComplete();
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  } catch (error) {
    console.error("Error in streaming chat:", error);
    onError(error);
  }
};