import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'
import CareerView from '@/views/CareerView.vue'
import ContactsView from '@/views/ContactsView.vue'
import StoresView from '@/views/StoresView.vue'
import GiftCardsView from '@/views/GiftCardsView.vue'
import CatalogView from '@/views/CatalogView.vue'
import ProductView from '@/views/ProductView.vue'
import PromotionsView from '@/views/PromotionsView.vue'
import SaleView from '@/views/SaleView.vue'
const router = createRouter({
    history: createWebHistory(),

    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },

        {
            path: '/about',
            name: 'about',
            component: AboutView
        },

        {
            path: '/career',
            name: 'career',
            component: CareerView
        },

        {
            path: '/contacts',
            name: 'contacts',
            component: ContactsView
        },

        {
            path: '/stores',
            name: 'stores',
            component: StoresView
        },

        {
            path: '/gift-cards',
            name: 'giftCards',
            component: GiftCardsView
        },

        {
            path: '/catalog',
            name: 'catalog',
            component: CatalogView
        },

        {
            path: '/product/:id',
            name: 'product',
            component: ProductView
        },

        {
            path: '/promotions',
            name: 'promotions',
            component: PromotionsView
        },
        {
        path: '/sale/:id',
        name: 'sale',
        component: SaleView
        }
    ]
})

export default router