/**
 * Centralized Service for The Internet's Most Unnecessary Search Engine
 * Abstracted HTTP layer connecting UI to backend /search endpoint.
 */

const CONFIG = {
  API_BASE_URL: (typeof window !== 'undefined' && window.__VITE_API_BASE_URL__) 
    || (window.location.port === '8000' ? '' : 'http://localhost:8000'),
  USE_MOCK_API: (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('mock') === 'true') || false,
  TIMEOUT_MS: 25000,
};

export const searchEngineAPI = {
  /**
   * Search an innocent question and receive escalating absurdities.
   * @param {string} query
   * @returns {Promise<SearchResponse>}
   */
  async search(query) {
    const cleanQuery = query.trim();
    if (!cleanQuery) {
      throw new Error("Please enter a question to overthink.");
    }

    if (CONFIG.USE_MOCK_API) {
      console.info("[API Service] Mock mode active. Generating synthetic response.");
      await new Promise(r => setTimeout(r, 900));
      return this.generateMockResponse(cleanQuery);
    }

    const endpoint = `${CONFIG.API_BASE_URL}/search`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT_MS);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ query: cleanQuery }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorDetail = `Server returned HTTP ${response.status}`;
        try {
          const errJson = await response.json();
          if (errJson.detail) {
            errorDetail = typeof errJson.detail === 'string' 
              ? errJson.detail 
              : errJson.detail[0]?.msg || errorDetail;
          }
        } catch (_) {}
        throw new Error(errorDetail);
      }

      const data = await response.json();
      return data;

    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error("The unnecessary intelligence engine took too long overthinking your question.");
      }
      throw err;
    }
  },

  /**
   * Generates a deterministic mock response for testing and offline presentations.
   */
  generateMockResponse(query) {
    return {
      query: query,
      results: [
        { rank: 1, tier: 1, title: "Mundane Reality", text: "They were briefly distracted by an ordinary, boring circumstance with zero hidden motives.", probability: 41, absurdity: 0.12 },
        { rank: 2, tier: 2, title: "Mild Paranoia", text: "They noticed a micro-hesitation in your delivery and decided to hedge defensively.", probability: 28, absurdity: 0.35 },
        { rank: 3, tier: 3, title: "Overanalyzed Vortex", text: "Both parties entered a recursive loop of mutual second-guessing and hyper-polite avoidance.", probability: 18, absurdity: 0.58 },
        { rank: 4, tier: 4, title: "Conspiracy Grade", text: "A clandestine focus group is currently logging your psychological micro-reactions.", probability: 9, absurdity: 0.81 },
        { rank: 5, tier: 5, title: "Multiverse Catastrophe", text: "A micro-rift in spacetime swapped your reality with one where this question controls quantum gravity.", probability: 4, absurdity: 0.96 }
      ],
      recommendation: "DO NOTHING. (Or speak exclusively in ancient riddles for the next 72 hours).",
      confidence: "99.2% Unearned Certainty",
      uselessness_score: 88,
      engine: "Autonomous Deduction Matrix"
    };
  }
};
