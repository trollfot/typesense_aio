class TestMetrics:

    async def test_get_metrics(self, typesense):
        result = await typesense.get_metrics()
        assert set(result) == {
            'system_cpu1_active_percentage',
            'system_cpu2_active_percentage',
            'system_cpu3_active_percentage',
            'system_cpu4_active_percentage',
            'system_cpu5_active_percentage',
            'system_cpu6_active_percentage',
            'system_cpu7_active_percentage',
            'system_cpu8_active_percentage',
            'system_cpu_active_percentage',
            'system_disk_total_bytes',
            'system_disk_used_bytes',
            'system_memory_total_bytes',
            'system_memory_used_bytes',
            'system_network_received_bytes',
            'system_network_sent_bytes',
            'typesense_memory_active_bytes',
            'typesense_memory_allocated_bytes',
            'typesense_memory_fragmentation_ratio',
            'typesense_memory_mapped_bytes',
            'typesense_memory_metadata_bytes',
            'typesense_memory_resident_bytes',
            'typesense_memory_retained_bytes'
        }
