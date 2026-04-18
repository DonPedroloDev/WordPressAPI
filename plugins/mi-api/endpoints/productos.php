<?php
/**
 * Endpoints REST para productos de WooCommerce.
 *
 * @package mi-api
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Registra las rutas REST de productos.
 */
function mi_api_registrar_rutas_productos(): void {
	register_rest_route(
		'mi-api/v1',
		'/productos',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'mi_api_obtener_productos',
			'permission_callback' => '__return_true',
			'args'                => array(
				'per_page' => array(
					'default'           => 10,
					'sanitize_callback' => 'absint',
				),
				'page'     => array(
					'default'           => 1,
					'sanitize_callback' => 'absint',
				),
			),
		)
	);

	register_rest_route(
		'mi-api/v1',
		'/productos/(?P<id>\\d+)',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'mi_api_obtener_producto_por_id',
			'permission_callback' => '__return_true',
		)
	);
}
add_action( 'rest_api_init', 'mi_api_registrar_rutas_productos' );

/**
 * Verifica si WooCommerce se encuentra activo.
 */
function mi_api_woocommerce_activo(): bool {
	return class_exists( 'WooCommerce' ) && function_exists( 'wc_get_product' );
}

/**
 * Da formato de respuesta a un producto.
 */
function mi_api_formatear_producto( WC_Product $producto ): array {
	$imagen_id  = $producto->get_image_id();
	$imagen_url = $imagen_id ? wp_get_attachment_image_url( $imagen_id, 'full' ) : '';
	$categorias = wp_get_post_terms( $producto->get_id(), 'product_cat', array( 'fields' => 'names' ) );

	if ( is_wp_error( $categorias ) ) {
		$categorias = array();
	}

	return array(
		'id'         => $producto->get_id(),
		'nombre'     => $producto->get_name(),
		'descripcion'=> wp_strip_all_tags( (string) $producto->get_description() ),
		'precio'     => (string) $producto->get_price(),
		'stock'      => (string) $producto->get_stock_status(),
		'imagen'     => $imagen_url ?: '',
		'categorias' => array_values( $categorias ),
	);
}

/**
 * Obtiene una lista paginada de productos publicados.
 */
function mi_api_obtener_productos( WP_REST_Request $request ): WP_REST_Response|WP_Error {
	if ( ! mi_api_woocommerce_activo() ) {
		return new WP_Error(
			'mi_api_woocommerce_inactivo',
			'WooCommerce no est\u00e1 activo.',
			array( 'status' => 500 )
		);
	}

	$per_page = max( 1, (int) $request->get_param( 'per_page' ) );
	$page     = max( 1, (int) $request->get_param( 'page' ) );

	$query = new WP_Query(
		array(
			'post_type'      => 'product',
			'post_status'    => 'publish',
			'posts_per_page' => $per_page,
			'paged'          => $page,
		)
	);

	$productos = array();

	foreach ( $query->posts as $post ) {
		$producto = wc_get_product( (int) $post->ID );

		if ( ! $producto ) {
			continue;
		}

		$productos[] = mi_api_formatear_producto( $producto );
	}

	$response = new WP_REST_Response( $productos, 200 );
	$response->header( 'X-Total', (string) $query->found_posts );
	$response->header( 'X-Total-Pages', (string) $query->max_num_pages );

	return $response;
}

/**
 * Obtiene un producto por ID.
 */
function mi_api_obtener_producto_por_id( WP_REST_Request $request ): WP_REST_Response|WP_Error {
	if ( ! mi_api_woocommerce_activo() ) {
		return new WP_Error(
			'mi_api_woocommerce_inactivo',
			'WooCommerce no est\u00e1 activo.',
			array( 'status' => 500 )
		);
	}

	$id       = (int) $request->get_param( 'id' );
	$producto = wc_get_product( $id );

	if ( ! $producto || 'publish' !== get_post_status( $producto->get_id() ) ) {
		return new WP_REST_Response(
			array(
				'code'    => 'mi_api_producto_no_encontrado',
				'message' => 'Producto no encontrado.',
			),
			404
		);
	}

	return new WP_REST_Response( mi_api_formatear_producto( $producto ), 200 );
}
