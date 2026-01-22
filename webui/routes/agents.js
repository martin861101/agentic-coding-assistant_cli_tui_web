// AI Agents API routes
import express from 'express';

const router = express.Router();

// Agent definitions
const agents = [
  {
    id: 'code-review',
    name: 'Code Review Agent',
    description: 'Analyzes code for bugs, security issues, and best practices',
    capabilities: ['analyze', 'review', 'security', 'best-practices'],
    systemPrompt: 'You are an expert code reviewer. Analyze code for bugs, security vulnerabilities, performance problems, and best practices.',
    color: '#7c3aed'
  },
  {
    id: 'refactoring',
    name: 'Refactoring Agent', 
    description: 'Improves code structure, applies SOLID principles',
    capabilities: ['refactor', 'restructure', 'solid', 'patterns'],
    systemPrompt: 'You are an expert at code refactoring. Improve code structure, apply SOLID principles, reduce complexity.',
    color: '#06b6d4'
  },
  {
    id: 'debugging',
    name: 'Debug Agent',
    description: 'Helps identify and fix bugs with intelligent analysis',
    capabilities: ['debug', 'trace', 'fix', 'analyze-error'],
    systemPrompt: 'You are an expert debugger. Analyze errors, identify root causes, suggest fixes.',
    color: '#ef4444'
  },
  {
    id: 'testing',
    name: 'Test Generation Agent',
    description: 'Generates comprehensive unit tests and test cases',
    capabilities: ['test', 'coverage', 'unit-test', 'integration-test'],
    systemPrompt: 'You are an expert at writing tests. Create comprehensive unit tests with good coverage.',
    color: '#10b981'
  },
  {
    id: 'documentation',
    name: 'Documentation Agent',
    description: 'Generates documentation and code comments',
    capabilities: ['document', 'comment', 'explain', 'readme'],
    systemPrompt: 'You are an expert technical writer. Create clear documentation and code comments.',
    color: '#f59e0b'
  },
  {
    id: 'architect',
    name: 'Architecture Agent',
    description: 'Designs system architecture and project structure',
    capabilities: ['architecture', 'structure', 'design', 'planning'],
    systemPrompt: 'You are an expert software architect. Design scalable system architectures and plan project structures.',
    color: '#8b5cf6'
  },
  {
    id: 'performance',
    name: 'Performance Agent',
    description: 'Optimizes code for speed and efficiency',
    capabilities: ['optimize', 'performance', 'profiling', 'speed'],
    systemPrompt: 'You are an expert at performance optimization. Identify bottlenecks and suggest optimizations.',
    color: '#ec4899'
  },
  {
    id: 'security',
    name: 'Security Agent',
    description: 'Identifies security vulnerabilities and suggests fixes',
    capabilities: ['security', 'vulnerability', 'audit', 'penetration'],
    systemPrompt: 'You are an expert security analyst. Identify vulnerabilities and suggest security best practices.',
    color: '#f43f5e'
  }
];

export function createAgentRoutes() {
  router.get('/agents', (req, res) => {
    res.json({ agents });
  });

  router.get('/agents/:id', (req, res) => {
    const agent = agents.find(a => a.id === req.params.id);
    if (!agent) return res.status(404).json({ error: 'Agent not found' });
    res.json(agent);
  });

  router.post('/ai/chat', async (req, res) => {
    try {
      const { message, context, agentId } = req.body;
      
      const agent = agentId ? agents.find(a => a.id === agentId) : null;
      
      const response = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: generateAIResponse(message, agent),
        timestamp: Date.now(),
        agent: agent?.name || 'ARIA'
      };
      
      res.json(response);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  return router;
}

function generateAIResponse(message, agent) {
  const lowerMessage = message.toLowerCase();
  
  if (agent) {
    return `[${agent.name}] I've analyzed your request. ${agent.systemPrompt.split('.')[0]}. How would you like me to proceed?`;
  }
  
  if (lowerMessage.includes('explain')) {
    return "I'd be happy to explain! Based on the code context, I can see several important patterns being used. Would you like me to go into detail about any specific part?";
  }
  
  if (lowerMessage.includes('refactor')) {
    return "I can suggest some refactoring improvements:\n\n1. Extract repeated logic into reusable functions\n2. Use more descriptive variable names\n3. Add error handling where missing\n\nWould you like me to implement any of these?";
  }
  
  return `I understand you're asking about: "${message}". I'm here to help with code review, refactoring, debugging, testing, and documentation. What specific aspect would you like me to focus on?`;
}

export { agents };
export default router;
