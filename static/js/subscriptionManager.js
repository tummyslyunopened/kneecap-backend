import ApiService from "./apiService.js";
import {CONSTANTS, state} from "./base.js";
import { safeGetElement } from "./utils.js";

class SubscriptionManager {
    async deleteSubscription(subscriptionId){
        try{
            await ApiService.idMethod(CONSTANTS.API_URLS.DELETE_SUBSCRIPTION, subscriptionId);
            const element = safeGetElement(subscriptionId);
            if (element) {
                element.remove();
            }
        } catch (error) {
        }
    }
}

export default SubscriptionManager