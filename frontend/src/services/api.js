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
        { rank: 1, tier: 1, title: "Mundane Reality", text: "They were holding two lukewarm coffees and a grocery bag with a snapped handle, typed using only their chin, and immediately forgot you exist.", probability: 41, absurdity: 0.12 },
        { rank: 2, tier: 2, title: "Mild Paranoia", text: "They drafted a warm 3-sentence reply, noticed it contained an exclamation mark, felt sickeningly vulnerable, deleted everything, and sent a single monosyllable to re-establish emotional dominance.", probability: 28, absurdity: 0.35 },
        { rank: 3, tier: 3, title: "The Overthought Spiral", text: "They read a LinkedIn article in 2017 about 'executive presence' and have spent the last seven years slowly incinerating their personal relationships one stone-cold reply at a time.", probability: 18, absurdity: 0.58 },
        { rank: 4, tier: 4, title: "Suspiciously Specific Plot", text: "They are auditioning for the role of a disillusioned Swedish detective in a bleak Nordic noir series and are method-acting emotional detachment across all incoming text messages.", probability: 9, absurdity: 0.81 },
        { rank: 5, tier: 5, title: "Completely Unhinged", text: "Their phone was momentarily commandeered by an eccentric raccoon that lives behind their garage and only knows how to accept invitations to social gatherings it has no intention of attending.", probability: 4, absurdity: 0.96 }
      ],
      recommendation: "DO NOTHING. In fact, do less than nothing. Leave your phone face-down on a wooden coaster, stare blankly at a floor lamp for 42 minutes, and let the awkwardness ripen into a fine vintage.",
      confidence: "104% Unearned Certainty",
      uselessness_score: 93,
      engine: "Autonomous Deduction Matrix"
    };
  }
};
