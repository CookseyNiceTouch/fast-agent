import { useState, useEffect, useRef } from "react";
import "./App.css";
import "./ChatUI.css";
import { FastAgentService, AgentRequest } from "./services/fastAgentService";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

function App() {
  const [message, setMessage] = useState("");
  const [agents, setAgents] = useState<string[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [selectedAgent, setSelectedAgent] = useState("default");
  const [selectedModel, setSelectedModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [chat, setChat] = useState<Message[]>([]);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch available agents and models on load
    const fetchData = async () => {
      try {
        const agentsList = await FastAgentService.getAgents();
        setAgents(agentsList);

        const modelsList = await FastAgentService.getModels();
        setModels(modelsList);
      } catch (error) {
        console.error("Error fetching initial data:", error);
        setChat((prev) => [
          ...prev,
          {
            role: "system",
            content:
              "Error connecting to Fast Agent backend. Make sure the API is running.",
          },
        ]);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    // Scroll to bottom whenever chat updates
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [chat]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message to chat
    setChat((prev) => [...prev, { role: "user", content: message }]);

    const request: AgentRequest = {
      message,
      agent: selectedAgent,
      model: selectedModel || undefined,
    };

    setLoading(true);
    setMessage("");

    try {
      const result = await FastAgentService.sendMessage(request);

      // Add agent response to chat
      setChat((prev) => [...prev, { role: "assistant", content: result }]);
    } catch (error) {
      console.error("Error:", error);
      setChat((prev) => [
        ...prev,
        {
          role: "system",
          content: "Error processing request. Check the console for details.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Fast Agent Desktop</h1>

      <div className="controls">
        <div className="select-container">
          <label>Agent:</label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
          >
            {agents.map((agent) => (
              <option key={agent} value={agent}>
                {agent}
              </option>
            ))}
          </select>
        </div>

        <div className="select-container">
          <label>Model:</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="">Default</option>
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="chat-container" ref={chatContainerRef}>
        <div className="messages-container">
          {chat.length === 0 && (
            <div className="message system">
              Start a conversation with the agent
            </div>
          )}
          {chat.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {loading && <div className="message system">Thinking...</div>}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          className="chat-input"
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="send-button"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
