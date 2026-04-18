<?php

/**
 * Plugin Name: Mi API
 * Description: API personalizada para WordPress y WooCommerce.
 * Version: 1.0.0
 * Requires PHP: 8.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// Carga los endpoints REST del plugin.
$mi_api_productos_endpoint = __DIR__ . '/mi-api/endpoints/productos.php';

if ( file_exists( $mi_api_productos_endpoint ) ) {
	require_once $mi_api_productos_endpoint;
}
