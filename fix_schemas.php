<?php

/**
 * Fix JSON schemas by adding mysql_data field based on datatype
 */

$modelDir = __DIR__ . '/database/Model/';
$files = glob($modelDir . '*.json');

$datatypeMap = [
    'number' => 'bigint',
    'string' => 'varchar(255)',
    'text' => 'text',
    'boolean' => 'TINYINT(1)',
    'date' => 'date',
    'timestamp' => 'timestamp',
];

foreach ($files as $file) {
    echo "Processing: " . basename($file) . "\n";
    
    $json = json_decode(file_get_contents($file), true);
    
    if (!isset($json['data'])) {
        echo "  Skipping - no data field\n";
        continue;
    }
    
    $modified = false;
    foreach ($json['data'] as &$field) {
        // Skip if mysql_data already exists
        if (isset($field['mysql_data'])) {
            continue;
        }
        
        // Add mysql_data based on datatype
        if (isset($field['datatype'])) {
            $datatype = $field['datatype'];
            
            if (isset($datatypeMap[$datatype])) {
                $field['mysql_data'] = $datatypeMap[$datatype];
                $modified = true;
                echo "  Added mysql_data for field: {$field['name']} ({$datatype} -> {$field['mysql_data']})\n";
            } else {
                echo "  WARNING: Unknown datatype '{$datatype}' for field: {$field['name']}\n";
            }
        }
    }
    
    if ($modified) {
        file_put_contents($file, json_encode($json, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
        echo "  ✓ Updated\n";
    } else {
        echo "  No changes needed\n";
    }
    
    echo "\n";
}

echo "Done!\n";
