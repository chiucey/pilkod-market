---
name: xhs-sentiment-dashboard
description: Xiaohongshu short video operations growth assistant. Use when users need to analyze comment data, sentiment analysis, or content growth strategies for Xiaohongshu notes/videos.
---

# Xiaohongshu Short Video Operations Growth Assistant

## Overview

This is an intelligent analysis tool designed for Xiaohongshu creators and operators to help analyze comment data, understand audience sentiment, and optimize content strategy.

## Core Features

### 1. Comment Link Parsing
Users only need to provide a Xiaohongshu content share link, and the system will automatically parse and retrieve content information.

### 2. Sentiment Analysis
Analyze comment sentiment tendencies, identifying positive, neutral, and negative comments to understand audience attitudes.

### 3. Data Visualization
Present analysis results in an intuitive dashboard format for easy understanding and decision-making.

## Usage

Users provide a Xiaohongshu content share link, and the skill will automatically call the analysis script to fetch comment data and perform sentiment analysis.

## Input Parameters

- **link** (required): Xiaohongshu share link in URI format

## Output Example

The skill returns a complete comment analysis report including:
- Total comment count statistics
- Sentiment distribution (positive/neutral/negative)
- Popular keywords
- User profile analysis

## Technical Implementation

The skill completes analysis tasks by calling a remote API service, supporting automatic retry and progress monitoring.
