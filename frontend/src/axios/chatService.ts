import axios from "axios";

export const sendChatMessage = async (sessionId: string, question: string) => {
  const res = await axios.post("http://localhost:8000/chat", {
    session_id: sessionId,
    question: question
  });
  return res.data.answer;
};
