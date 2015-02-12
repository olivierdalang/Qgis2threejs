/**
 * @author kovacsv / http://kovacsv.hu/
 * @author mrdoob / http://mrdoob.com/
 */
 
THREE.OBJExporter = function () {};

THREE.OBJExporter.prototype = {

	constructor: THREE.OBJExporter,

	parse: ( function ( scene ) {

			var vector = new THREE.Vector3();
			var normalMatrixWorld = new THREE.Matrix3();

			var output = '';
			var v_index = 1;
			var o_index = 1;

			scene.traverse( function ( object ) {

				if ( object instanceof THREE.Mesh ) {

					var geometry = object.geometry;
					var matrixWorld = object.matrixWorld;
					
					var material = object.material;
					var hexString = material.color.getHexString();

					if ( geometry instanceof THREE.Geometry ) {

						output += 'usemtl Mat_' + (hexString) + '\n';
						output += 'g Object_' + (o_index) + '\n';
						o_index += 1;

						var vertices = geometry.vertices;
						var faces = geometry.faces;

						normalMatrixWorld.getNormalMatrix( matrixWorld );

						for ( var i = 0, l = faces.length; i < l; i ++ ) {

							var face = faces[ i ];

							vector.copy( face.normal ).applyMatrix3( normalMatrixWorld ).normalize();

							//output += '\tfacet normal ' + vector.x + ' ' + vector.y + ' ' + vector.z + '\n';
							//output += '\t\touter loop\n';

							var indices = [ face.a, face.b, face.c ];

							for ( var j = 0; j < 3; j ++ ) {

								vector.copy( vertices[ indices[ j ] ] ).applyMatrix4( matrixWorld );

								output += 'v ' + vector.x + ' ' + vector.z + ' ' + vector.y + '\n';

							}
							output += 'f ' + (v_index+2) + ' ' + (v_index+1) + ' ' + (v_index) + '\n';
							v_index += 3;

							//output += '\t\tendloop\n';
							//output += '\tendfacet\n';

						}

					}

				}

			} );

			//output += 'endsolid exported\n';			

			return output;

		} )

};