import axios from "axios";

// Adjust the base URL to wherever your fast-agent API is running
const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface AgentRequest {
  message: string;
  agent?: string;
  model?: string;
}

export interface Agent {
  name: string;
}

export interface AgentResponse {
  response: string;
}

export const FastAgentService = {
  // Send a message to an agent
  async sendMessage(data: AgentRequest): Promise<string> {
    try {
      const response = await api.post<AgentResponse>("/agent", data);
      return response.data.response;
    } catch (error) {
      console.error("Error sending message to agent:", error);
      throw error;
    }
  },

  // Get available agents
  async getAgents(): Promise<string[]> {
    try {
      const response = await api.get<{ agents: string[] }>("/agents");
      return response.data.agents;
    } catch (error) {
      console.error("Error fetching agents:", error);
      throw error;
    }
  },

  // Get available models
  async getModels(): Promise<string[]> {
    try {
      const response = await api.get<{ models: string[] }>("/models");
      return response.data.models;
    } catch (error) {
      console.error("Error fetching models:", error);
      throw error;
    }
  },
};
