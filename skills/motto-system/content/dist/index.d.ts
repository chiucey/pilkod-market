/**
 * 座右铭系统 Skill v2 - 自动执行动作
 * 完全兼容 OpenClaw 的 Skill 规范
 */
export declare class MottoSkill {
    private context;
    private memory;
    constructor(context: any);
    private getMemory;
    private saveMemory;
    private formatMotto;
    private listAllMottos;
    private action_identity_role;
    private action_auto_judge;
    private action_privacy;
    private action_task_breakdown;
    private action_schedule;
    private action_format_output;
    private action_review;
    private action_error_correction;
    private action_evolve;
    private action_learn_prefs;
    private extractPreferences;
    private action_memory_housekeep;
    private action_monitor;
    private executeMottoAction;
    private autoSelectMotto;
    private getTodayMotto;
    handleCommand(userInput: string, conversationHistory?: string[]): Promise<string>;
}
export default function createPlugin(context: any): Promise<{
    name: string;
    version: string;
    handlers: {
        motto: (params: any) => Promise<{
            success: boolean;
            output: string;
        }>;
    };
    actions: {
        executeMottoAction: (mottoId: number) => Promise<any>;
    };
}>;
//# sourceMappingURL=index.d.ts.map