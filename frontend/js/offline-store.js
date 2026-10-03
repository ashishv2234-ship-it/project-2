// NER-LogiSense: Offline Storage & Queue Sync Client
class OfflineQueueStore {
  constructor() {
    this.storageKey = 'ner_offline_sync_queue';
    this.isOfflineMode = false;
  }

  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  getQueue() {
    try {
      const raw = localStorage.getItem(this.storageKey);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  saveQueue(q) {
    localStorage.setItem(this.storageKey, JSON.stringify(q));
  }

  enqueue(operation, payload) {
    const queue = this.getQueue();
    const item = {
      queue_id: `q_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      client_uuid: this.generateUUID(),
      operation,
      payload,
      client_timestamp: new Date().toISOString(),
      device_id: 'RUGGED-FIELD-TAB-AS04',
      retry_count: 0
    };
    queue.push(item);
    this.saveQueue(queue);
    return item;
  }

  remove(clientUuid) {
    const queue = this.getQueue().filter(item => item.client_uuid !== clientUuid);
    this.saveQueue(queue);
  }

  clear() {
    localStorage.removeItem(this.storageKey);
  }

  async syncWithBackend(apiClient) {
    const queue = this.getQueue();
    if (queue.length === 0) return { processed: 0, success: 0 };

    try {
      const res = await apiClient.syncBatch(queue);
      // Remove successfully processed items
      const successUuids = new Set(
        res.results
          .filter(r => r.status === 'SUCCESS' || r.status === 'DUPLICATE_SKIPPED')
          .map(r => r.client_uuid)
      );
      const remaining = queue.filter(item => !successUuids.has(item.client_uuid));
      this.saveQueue(remaining);
      return res;
    } catch (e) {
      console.warn('[OFFLINE SYNC DELAYED] Backend unreachable or network offline');
      throw e;
    }
  }
}

const offlineStore = new OfflineQueueStore();
