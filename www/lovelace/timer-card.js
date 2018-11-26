class CustomTimerCard extends HTMLElement {
    set hass(hass) {
      if (!this.content) {
        const card = document.createElement('ha-card');
        card.header = 'Timer';
        this.content = document.createElement('div');
        this.content.style.padding = '0 16px 16px';
        card.appendChild(this.content);
        this.appendChild(card);
      }
  
      const entityId = this.config.entity;
      const state = hass.states[entityId];
      const stateStr = state ? state.state : 'unavailable';

      var endDate = new Date();
      var startDate   = new Date(state.attributes['trigger_time']);
      var seconds = (endDate.getTime() - startDate.getTime()) / 1000;

  
      this.content.innerHTML = `
        ${entityId} is ${state.state} fires in ${seconds} on ${startDate}!
      `;
    }
  
    setConfig(config) {
      if (!config.entity) {
        throw new Error('You need to define an entity');
      }
      this.config = config;
    }
  
    // The height of your card. Home Assistant uses this to automatically
    // distribute all cards over the available columns.
    getCardSize() {
      return 3;
    }
  }
  
  customElements.define('custom-timer-card', CustomTimerCard);