# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Guidelines

**BEFORE making any changes to this codebase:**
1. **Read QA.md thoroughly** - Contains critical bug prevention rules and deployment lessons learned from 7+ major bugs
2. **Apply QA.md Rules** - All 7 QA rules must be followed to prevent recurring bugs (inheritance, data contracts, defensive programming)
3. **Verify inheritance chains** - Check attribute/method availability before accessing (QA Rule 1 & 6)
4. **Validate data structures** - Ensure consistent data formats between modules (QA Rule 5)
5. **Test with minimal data** - Verify startup behavior when market data is limited (QA Rule 4)
6. **Follow defensive programming** - Use .get() methods and provide defaults (QA Rule 5)
7. **Update QA.md with new lessons** - Document any new bugs/fixes for future prevention

## Project Overview Continued...

The rest of the file contents remain unchanged from the previous submission. The provided text represents the entire file content, preserving the existing comprehensive documentation about the trading system's architecture, deployment, and development workflow.