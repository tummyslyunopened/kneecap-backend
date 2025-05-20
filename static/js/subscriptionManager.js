import ApiService from "./apiService.js";
import { CONSTANTS } from "./base.js";
import { safeGetElement } from "./utils.js";

/**
 * SubscriptionManager - Handles all subscription-related operations
 * Provides methods for managing podcast subscriptions with proper error handling and user feedback
 */
class SubscriptionManager {
    /**
     * Deletes a subscription by its ID
     * @param {string|number} subscriptionId - The ID of the subscription to delete
     * @param {Object} [options] - Additional options
     * @param {boolean} [options.silent=false] - If true, suppresses success/error toasts
     * @returns {Promise<Object>} The API response
     */
    async deleteSubscription(subscriptionId, options = {}) {
        const { silent = false } = options;
        const element = safeGetElement(`subscription-${subscriptionId}`) || safeGetElement(subscriptionId);
        
        try {
            // Use the enhanced ApiService with proper error handling
            await ApiService.idMethod(
                CONSTANTS.API_URLS.DELETE_SUBSCRIPTION,
                subscriptionId,
                {
                    showSuccess: !silent,
                    showError: !silent,
                    successMessage: 'Subscription deleted successfully',
                    errorMessage: 'Failed to delete subscription',
                }
            );

            // If we get here, the deletion was successful
            if (element) {
                // Add a fade-out effect before removing
                element.style.transition = 'opacity 0.3s';
                element.style.opacity = '0';
                
                // Wait for the transition to complete before removing
                setTimeout(() => {
                    if (element && element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                }, 300);
            }
            
            return { success: true };
            
        } catch (error) {
            console.error('Error in deleteSubscription:', error);
            
            if (!silent) {
                // ApiService already shows the error toast, but we can add additional handling here
                // For example, you might want to show a more specific error message
                if (error.status === 404) {
                    console.warn('Subscription not found, it may have already been deleted');
                }
            }
            
            // Re-throw the error for the caller to handle if needed
            throw error;
        }
    }
    
    /**
     * Refreshes a subscription to fetch the latest episodes
     * @param {string|number} subscriptionId - The ID of the subscription to refresh
     * @returns {Promise<Object>} The API response
     */
    async refreshSubscription(subscriptionId) {
        try {
            return await ApiService.idMethod(
                CONSTANTS.API_URLS.REFRESH_SUBSCRIPTION,
                subscriptionId,
                {
                    successMessage: 'Subscription refreshed successfully',
                    errorMessage: 'Failed to refresh subscription'
                }
            );
        } catch (error) {
            console.error('Error refreshing subscription:', error);
            throw error;
        }
    }
    
    /**
     * Updates subscription settings
     * @param {string|number} subscriptionId - The ID of the subscription to update
     * @param {Object} updates - The updates to apply
     * @returns {Promise<Object>} The updated subscription
     */
    async updateSubscription(subscriptionId, updates) {
        try {
            return await ApiService.post(
                `${CONSTANTS.API_URLS.SUBSCRIPTIONS}/${subscriptionId}/`,
                updates,
                {
                    successMessage: 'Subscription updated successfully',
                    errorMessage: 'Failed to update subscription'
                }
            );
        } catch (error) {
            console.error('Error updating subscription:', error);
            throw error;
        }
    }
}

export default SubscriptionManager;