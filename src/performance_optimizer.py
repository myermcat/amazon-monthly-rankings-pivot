#!/usr/bin/env python3
"""
Performance Optimization Module for the Amazon Monthly Rankings Pivot Table System.
Handles large datasets efficiently with memory management and optimization techniques.
"""

import pandas as pd
import numpy as np
import gc
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import psutil
import os
import sys

class PerformanceOptimizer:
    """
    Optimizes performance for large pivot table operations.
    Handles memory management, data chunking, and efficient processing.
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.memory_threshold = 0.8  # 80% memory usage threshold
        self.chunk_size = 10000  # Process data in chunks of 10k rows
        self.optimization_level = "balanced"  # balanced, memory, speed
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Get system memory
        system_memory = psutil.virtual_memory()
        
        return {
            'process_memory_mb': memory_info.rss / 1024 / 1024,
            'system_memory_percent': system_memory.percent,
            'system_memory_available_gb': system_memory.available / 1024 / 1024 / 1024,
            'system_memory_total_gb': system_memory.total / 1024 / 1024 / 1024
        }
    
    def check_memory_pressure(self) -> bool:
        """Check if system is under memory pressure."""
        memory_info = self.get_memory_usage()
        return memory_info['system_memory_percent'] > (self.memory_threshold * 100)
    
    def optimize_dataframe(self, df: pd.DataFrame, optimization_level: str = None) -> pd.DataFrame:
        """
        Optimize DataFrame for memory usage and performance.
        
        Args:
            df: DataFrame to optimize
            optimization_level: 'memory', 'speed', or 'balanced'
            
        Returns:
            Optimized DataFrame
        """
        if optimization_level is None:
            optimization_level = self.optimization_level
            
        print(f"🔧 Optimizing DataFrame ({df.shape}) with {optimization_level} strategy...")
        
        start_memory = self.get_memory_usage()['process_memory_mb']
        
        # Make a copy to avoid modifying original
        optimized_df = df.copy()
        
        if optimization_level in ['memory', 'balanced']:
            # Memory optimization
            optimized_df = self._optimize_memory_usage(optimized_df)
            
        if optimization_level in ['speed', 'balanced']:
            # Speed optimization
            optimized_df = self._optimize_speed(optimized_df)
            
        end_memory = self.get_memory_usage()['process_memory_mb']
        memory_saved = start_memory - end_memory
        
        print(f"✅ Optimization complete! Memory saved: {memory_saved:.2f} MB")
        return optimized_df
    
    def _optimize_memory_usage(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame for memory usage."""
        print("  💾 Applying memory optimizations...")
        
        for col in df.columns:
            col_type = df[col].dtype
            
            # Optimize numeric columns
            if np.issubdtype(col_type, np.number):
                if col_type == np.float64:
                    # Check if we can use float32
                    if df[col].notna().all() and df[col].between(-3.4e38, 3.4e38).all():
                        df[col] = df[col].astype(np.float32)
                        print(f"    {col}: float64 → float32")
                elif col_type == np.int64:
                    # Check if we can use smaller int types
                    col_min, col_max = df[col].min(), df[col].max()
                    if col_min >= -32768 and col_max <= 32767:
                        df[col] = df[col].astype(np.int16)
                        print(f"    {col}: int64 → int16")
                    elif col_min >= -2147483648 and col_max <= 2147483647:
                        df[col] = df[col].astype(np.int32)
                        print(f"    {col}: int64 → int32")
            
            # Optimize object columns (strings)
            elif col_type == 'object':
                # Check if we can use category type
                unique_ratio = df[col].nunique() / len(df[col])
                if unique_ratio < 0.5:  # Less than 50% unique values
                    df[col] = df[col].astype('category')
                    print(f"    {col}: object → category")
        
        return df
    
    def _optimize_speed(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame for speed."""
        print("  ⚡ Applying speed optimizations...")
        
        # Set index for faster lookups if not already set
        if df.index.name != 'Search Term' and 'Search Term' in df.columns:
            df = df.set_index('Search Term')
            print("    Set Search Term as index for faster lookups")
        
        # Sort index for faster operations
        if df.index.is_monotonic_increasing:
            print("    Index already sorted")
        else:
            df = df.sort_index()
            print("    Sorted index for faster operations")
        
        return df
    
    def process_large_dataset(self, file_path: str, chunk_size: int = None) -> pd.DataFrame:
        """
        Process large CSV files in chunks to manage memory.
        
        Args:
            file_path: Path to CSV file
            chunk_size: Number of rows to process at once
            
        Returns:
            Combined DataFrame
        """
        if chunk_size is None:
            chunk_size = self.chunk_size
            
        print(f"📁 Processing large dataset: {file_path}")
        print(f"  Chunk size: {chunk_size:,} rows")
        
        # Get file size
        file_size_mb = Path(file_path).stat().st_size / 1024 / 1024
        print(f"  File size: {file_size_mb:.2f} MB")
        
        # Check if chunking is needed
        if file_size_mb < 100:  # Less than 100MB, load normally
            print("  File is small enough to load normally")
            return pd.read_csv(file_path, skiprows=1)
        
        print("  Using chunked processing for large file...")
        
        chunks = []
        total_rows = 0
        
        # Process in chunks
        for chunk_num, chunk in enumerate(pd.read_csv(file_path, skiprows=1, chunksize=chunk_size)):
            chunks.append(chunk)
            total_rows += len(chunk)
            
            # Memory check
            if self.check_memory_pressure():
                print(f"    ⚠️  Memory pressure detected at chunk {chunk_num + 1}")
                # Force garbage collection
                gc.collect()
            
            if chunk_num % 10 == 0:  # Progress update every 10 chunks
                print(f"    Processed {chunk_num + 1} chunks, {total_rows:,} rows")
        
        print(f"  ✅ Chunked processing complete: {len(chunks)} chunks, {total_rows:,} total rows")
        
        # Combine chunks
        print("  🔗 Combining chunks...")
        combined_df = pd.concat(chunks, ignore_index=True)
        
        # Clean up chunks to free memory
        del chunks
        gc.collect()
        
        print(f"  ✅ Dataset processing complete: {combined_df.shape}")
        return combined_df
    
    def optimize_table_operations(self, df: pd.DataFrame, operation: str) -> pd.DataFrame:
        """
        Optimize specific table operations.
        
        Args:
            df: DataFrame to optimize
            operation: Type of operation ('merge', 'concat', 'groupby', etc.)
            
        Returns:
            Optimized DataFrame
        """
        print(f"🔧 Optimizing for {operation} operation...")
        
        if operation == 'merge':
            # Optimize for merge operations
            if df.index.name != 'Search Term':
                df = df.set_index('Search Term')
            df = df.sort_index()
            
        elif operation == 'concat':
            # Optimize for concatenation
            df = df.reset_index(drop=True)
            
        elif operation == 'groupby':
            # Optimize for groupby operations
            df = df.sort_values('Search Term')
            
        print(f"  ✅ Optimization for {operation} complete")
        return df
    
    def monitor_performance(self, operation_name: str, start_time: float = None) -> float:
        """
        Monitor performance of operations.
        
        Args:
            operation_name: Name of the operation being monitored
            start_time: Start time (if None, starts monitoring now)
            
        Returns:
            Elapsed time in seconds
        """
        if start_time is None:
            start_time = time.time()
            return start_time
        
        elapsed_time = time.time() - start_time
        memory_usage = self.get_memory_usage()
        
        print(f"⏱️  {operation_name} completed in {elapsed_time:.2f} seconds")
        print(f"   Memory usage: {memory_usage['process_memory_mb']:.2f} MB")
        print(f"   System memory: {memory_usage['system_memory_percent']:.1f}%")
        
        return elapsed_time
    
    def get_optimization_recommendations(self, df: pd.DataFrame) -> List[str]:
        """
        Get recommendations for optimizing the DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Memory usage analysis
        memory_usage = df.memory_usage(deep=True)
        total_memory = memory_usage.sum() / 1024 / 1024  # MB
        
        if total_memory > 100:  # More than 100MB
            recommendations.append(f"Consider chunked processing for large dataset ({total_memory:.1f} MB)")
        
        # Data type analysis
        for col in df.columns:
            col_type = df[col].dtype
            col_memory = memory_usage[col] / 1024 / 1024  # MB
            
            if col_type == 'object' and col_memory > 10:
                unique_ratio = df[col].nunique() / len(df[col])
                if unique_ratio < 0.3:
                    recommendations.append(f"Convert '{col}' to category type (memory: {col_memory:.1f} MB)")
            
            elif col_type == np.float64 and col_memory > 5:
                recommendations.append(f"Consider float32 for '{col}' (memory: {col_memory:.1f} MB)")
            
            elif col_type == np.int64 and col_memory > 5:
                recommendations.append(f"Consider smaller int type for '{col}' (memory: {col_memory:.1f} MB)")
        
        # Index optimization
        if df.index.name != 'Search Term':
            recommendations.append("Set 'Search Term' as index for faster lookups")
        
        if not df.index.is_monotonic_increasing:
            recommendations.append("Sort index for faster operations")
        
        return recommendations

def create_performance_profile() -> Dict[str, any]:
    """Create a performance profile for the current system."""
    optimizer = PerformanceOptimizer()
    
    profile = {
        'memory_usage': optimizer.get_memory_usage(),
        'optimization_settings': {
            'memory_threshold': optimizer.memory_threshold,
            'chunk_size': optimizer.chunk_size,
            'optimization_level': optimizer.optimization_level
        },
        'system_info': {
            'cpu_count': os.cpu_count(),
            'python_version': sys.version,
            'pandas_version': pd.__version__,
            'numpy_version': np.__version__
        }
    }
    
    return profile

if __name__ == "__main__":
    print("🔧 Performance Optimizer Module")
    print("=" * 40)
    
    # Create performance profile
    profile = create_performance_profile()
    
    print(f"📊 System Performance Profile:")
    print(f"  CPU Cores: {profile['system_info']['cpu_count']}")
    print(f"  Python: {profile['system_info']['python_version'].split()[0]}")
    print(f"  Pandas: {profile['system_info']['pandas_version']}")
    print(f"  NumPy: {profile['system_info']['numpy_version']}")
    
    print(f"\n💾 Memory Settings:")
    print(f"  Memory Threshold: {profile['optimization_settings']['memory_threshold'] * 100}%")
    print(f"  Chunk Size: {profile['optimization_settings']['chunk_size']:,} rows")
    print(f"  Optimization Level: {profile['optimization_settings']['optimization_level']}")
    
    print(f"\n🚀 Performance Optimizer ready for use!")
