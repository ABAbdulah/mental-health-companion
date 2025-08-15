import { useState, useEffect } from "react";

const texts = [
  "Hi, I'm Abdullah's personal chatbot.",
  "Ask me anything about Abdullah!",
  "Your questions, my answers — instantly."
];

export default function IntroText() {
  const [lines, setLines] = useState<string[]>([]); // stores all completed lines
  const [currentText, setCurrentText] = useState("");
  const [index, setIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (index < texts.length) {
      if (charIndex < texts[index].length) {
        const timeout = setTimeout(() => {
          setCurrentText((prev) => prev + texts[index][charIndex]);
          setCharIndex(charIndex + 1);
        }, 50);
        return () => clearTimeout(timeout);
      } else {
        const timeout = setTimeout(() => {
          setLines((prev) => [...prev, texts[index]]);
          setCurrentText("");
          setCharIndex(0);
          setIndex(index + 1);
        }, 800);
        return () => clearTimeout(timeout);
      }
    }
  }, [charIndex, index]);

  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      {/* Fixed Title */}
      <h1 className="text-3xl font-bold mb-4 text-blue-600">AskAbdullah :)</h1>

      {/* Completed lines */}
      {lines.map((line, i) => (
        <p key={i} className="text-xl text-gray-700">{line}</p>
      ))}

      {/* Currently typing line */}
      {index < texts.length && (
        <p className="text-xl text-gray-700">{currentText}</p>
      )}
    </div>
  );
}
